import concurrent.futures
import timeout_decorator
import ast

from abc import ABC
from multiprocessing import current_process

from ..cfg import Graph, ScalpelError
from ..utils.utils import *

N_PROCESSES_DEFAULT = 4

TIMEOUT_LIMIT = 10#seconds

class SkeletonEncoder(ABC):
    """
    Class implementing methods for converting source code
    to a dictionary representing its Control Flow.
    """
    @staticmethod
    def from_sources(srclist:list, verbose:bool=False) -> list[dict]:
        """
        Takes a list of string of Python source code and returns a list 
        containing pairs of (src, their respective CFGs as a dictionary). 
        """
        result = []

        process = current_process().name.replace('Fork', '')

        total = len(srclist)

        timeout_errors = scalpel_errors = syntax_errors = 0 

        for i, src in enumerate(srclist): 
            if verbose: 
                count = i + 1; percentage = count * 100 / total
                print(process, f'{count}/{total} | {percentage:.1f}%', flush=True)

            try:     G = SkeletonEncoder.__get_cfg_timeout(src)
            except   TimeoutError:   timeout_errors += 1  ; continue
            except   ScalpelError:   scalpel_errors += 1  ; continue
            except   SyntaxError :   syntax_errors  += 1  ; continue
            finally: result.append((src, G.to_dict()))

        if verbose:
            errors = [syntax_errors, scalpel_errors, timeout_errors]
            print('\nERRORS SUMMARY:', flush=True)
            log_error(f'Syntax  errors: {errors[0]}.')
            log_error(f'Scalpel errors: {errors[1]}.')
            log_error(f'Timeout errors: {errors[2]}.')
            log_error(f'TOTAL: {sum(errors)} not processed.')

        return result

    @staticmethod
    def from_sources_parallel(
            srclist:list[str], n_processes:int=N_PROCESSES_DEFAULT, 
            verbose:bool=False
        ) -> list[dict]:
        """
        Same as `from_sources` but using `n_processes` to process the sources.
        """
        f = SkeletonEncoder.from_sources

        return SkeletonEncoder.__run_parallel(
            f, srclist, n_processes, verbose
        )

    @staticmethod
    def from_single_functions(
            functions:list[str], verbose:bool=False
        ) -> list[dict]:
        """
        Takes a list of string of Python single (non-nested) functions and 
        returns a list containing their respective CFGs as a dictionary. 
        """
        ok, not_ok = SkeletonEncoder.functions_sanity_check(functions)

        if verbose:
            print(f'{len(not_ok)} functions not processed', flush=True)

        result = []

        src_cfgs = SkeletonEncoder.from_sources(ok, verbose)

        # (function src, function cfg)
        for src, cfg in src_cfgs:
            if len(cfg['functions']) == 0: continue
            else: result.append((src, cfg['functions'][0]))

        return result

    @staticmethod
    def from_single_functions_parallel(
            functions:list[str], n_processes:int=N_PROCESSES_DEFAULT, 
            verbose:bool=False
        ) -> list[dict]:
        """
        Same as `from_single_functions` but using `n_processes` to process the 
        functions.
        """
        f = SkeletonEncoder.from_single_functions

        return SkeletonEncoder.__run_parallel(
            f, functions, n_processes, verbose
        )

    @staticmethod
    def from_files(files:list[str], verbose:bool=False) -> list[dict]:
        """
        Takes a list of filepaths to files containing Python source code and 
        returns a list containing their respective CFGs as a dictionary. 
        """
        srclist = []

        for file in files:
            with open(file) as f: src = f.read()
            srclist.append(src)
        
        return SkeletonEncoder.from_sources(srclist, verbose)

    @staticmethod
    def from_files_parallel(
            files:list[str], n_processes:int=N_PROCESSES_DEFAULT, 
            verbose:bool=False
        ) -> list[dict]:
        """
        Same as `from_files` but using `n_processes` to process the files.
        """
        f = SkeletonEncoder.from_files

        return SkeletonEncoder.__run_parallel(
            f, files, n_processes, verbose
        )


    @staticmethod
    def from_files_of_single_functions(
            files:list[str], verbose:bool=False
        ) -> list[dict]:
        """
        Takes a list of filepaths to files, each containing a single Python 
        (non-nested) function and returns a list containing their respective 
        CFGs as a dictionary. 
        """
        srclist = []

        for file in files:
            with open(file) as f: src = f.read()
            srclist.append(src)
        
        return SkeletonEncoder.from_single_functions(srclist, verbose)

    @staticmethod
    def from_files_of_single_functions_parallel(
            files:list[str], n_processes:int=4, verbose:bool=False
        ) -> list[dict]:
        """
        Same as `from_files_of_single_functions` but using `n_processes` 
        to process the files.
        """
        srclist = []

        for file in files:
            with open(file) as f: src = f.read()
            srclist.append(src)
        
        return SkeletonEncoder.from_single_functions_parallel(
            srclist, n_processes, verbose)


    @staticmethod
    def __split_buckets(list:list[str], n_processes:int):
        """
        To distribute work between the different `n_processes`.
        """
        buckets = [[] for _ in range(n_processes)]

        for i, src in enumerate(list):
            index = i % n_processes
            buckets[index].append(src)

        return buckets

    @staticmethod
    def function_sanity_check(function:str):
        """
        Performs a sanity check for a Python function, since we do 
        not support function containing nested functions or classes. 
        Returns True if function can be processed.
        """

        try: tree = ast.parse(function)
        except Exception: return False

        def has_one_FunctionDef(node:ast.AST, count=0):
            for child in ast.walk(node):
                if isinstance(child, ast.FunctionDef):
                    count += 1
            return count == 1

        C1 = function.count('class ') == 0 # nested classes
        C2 = has_one_FunctionDef(tree)

        return C1 and C2

    @staticmethod
    def functions_sanity_check(functions:list[str]):
        """
        Performs a sanity check for a list of Python functions, returns
        a tuple (can_process, can_not_process).
        """
        can_process, can_not_process = [], []
        for function in functions:
            if SkeletonEncoder.function_sanity_check(function):
                can_process.append(function)
            else: can_not_process.append(function)

        return can_process, can_not_process

    @timeout_decorator.timeout(seconds=TIMEOUT_LIMIT, timeout_exception=TimeoutError)
    def __get_cfg_timeout(src): return Graph(src)

    @staticmethod
    def __run_parallel(f, to_process:list, n_processes:int=4, verbose:bool=False):
        buckets = SkeletonEncoder.__split_buckets(to_process, n_processes)

        with concurrent.futures.ProcessPoolExecutor() as e:
            futures = [e.submit(f, b, verbose) for b in buckets]
            
        result = []
        for future in futures: result += future.result()
        return result