from abc import ABC
import concurrent.futures
import multiprocessing as mp
import timeout_decorator

from ..cfg import Graph, ScalpelError
from ..util import *

N_PROCESSES_DEFAULT = 4

TIMEOUT_LIMIT_DEFAULT = 30 #seconds

class SkeletonEncoder(ABC):
    """
    Abstract class containing methods for converting source code
    to a dictionary representing its Control Flow.
    """
    @staticmethod
    def from_sources(srclist:list, verbose:bool=False) -> list[dict]:
        """
        Takes a list of string of Python source code and returns a list 
        containing pairs of (src, their respective CFGs as a dictionary). 
        """
        process = mp.current_process().name.replace('Fork', '')
        N = len(srclist)
        
        result = []

        scalpel_errors = syntax_errors = timeout_errors = assertion_errors = 0 

        for i, src in enumerate(srclist): 
            if verbose: print(process, f'{i+1}/{N}', flush=True)

            # TODO: Handle errors.
            try: 
                G = SkeletonEncoder.__get_cfg(src)
            except SyntaxError: 
                syntax_errors += 1
                continue
            except ScalpelError: 
                scalpel_errors += 1
                continue
            except TimeoutError: 
                timeout_errors += 1
                continue
            except AssertionError:
                assertion_errors += 1
                continue

            result.append((src, G.to_dict()))

        if verbose:
            errors = [syntax_errors, scalpel_errors, 
                 timeout_errors, assertion_errors,]

            log_error(f'Syntax    errors: {errors[0]}.')
            log_error(f'Scalpel   errors: {errors[1]}.')
            log_error(f'Timeout   errors: {errors[2]}.')
            log_error(f'Assertion errors: {errors[3]}.')
            log_error(f'Total: {sum(errors)}.')

        return result

    @staticmethod
    def from_sources_parallel(
            srclist:list[str], n_processes:int=N_PROCESSES_DEFAULT, 
            verbose:bool=False
        ) -> list[dict]:
        """
        Same as `from_sources` but using `n_processes` to process the sources.
        """
        buckets = SkeletonEncoder.__split_buckets(srclist, n_processes)

        with concurrent.futures.ProcessPoolExecutor() as e:
            futures = [e.submit(SkeletonEncoder.from_sources, b, verbose) 
                        for b in buckets]
            
        result = []
        for future in futures: result += future.result()
        return result


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

        result = SkeletonEncoder.from_sources(ok, verbose)
        # (function src, function cfg)
        return [(_[0], _[1]['functions'][0]) for _ in result]

    @staticmethod
    def from_single_functions_parallel(
            functions:list[str], n_processes:int=N_PROCESSES_DEFAULT, 
            verbose:bool=False
        ) -> list[dict]:
        """
        Same as `from_single_functions` but using `n_processes` to process the 
        functions.
        """
        buckets = SkeletonEncoder.__split_buckets(functions, n_processes)

        with concurrent.futures.ProcessPoolExecutor() as e:
            futures = [e.submit(SkeletonEncoder.from_single_functions, b, verbose) 
                        for b in buckets]
            
        result = []
        for future in futures: result += future.result()
        return result


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
        buckets = SkeletonEncoder.__split_buckets(files, n_processes)

        with concurrent.futures.ProcessPoolExecutor() as e:
            futures = [e.submit(SkeletonEncoder.from_files, b, verbose) 
                        for b in buckets]
            
        result = []
        for future in futures: result += future.result()
        return result


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
        
        return SkeletonEncoder.from_single_functions_parallel(srclist, n_processes, verbose)


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
        return function.count('def ') == 1 and function.count('class ') == 0

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

    @timeout_decorator.timeout(TIMEOUT_LIMIT_DEFAULT)
    def __get_cfg(src): return Graph(src)