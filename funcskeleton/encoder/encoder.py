import concurrent.futures
import multiprocessing
import ast

from ..cfg import Graph

class Encoder(object):

    @staticmethod
    def dicts_from_sources(srclist:list, verbose=False):

        process = multiprocessing.current_process().name.replace('Fork', '')
        N = len(srclist)
        
        result = []

        for i, src in enumerate(srclist): 
            if verbose: print(process, f'{i+1}/{N}', flush=True)

            result.append(Graph(src).to_dict())

        return result

    @staticmethod
    def dicts_from_sources_parallel(srclist:list, n_processes=4, verbose=False):
        buckets = Encoder.__split_buckets(srclist, n_processes)

        with concurrent.futures.ProcessPoolExecutor() as e:
            futures = [e.submit(Encoder.dicts_from_sources, b, verbose) 
                        for b in buckets]
            
        result = []
        for future in futures: result += future.result()
        return result


    @staticmethod
    def dicts_from_single_functions(functions:list, verbose=False):
        functions = Encoder.__functions_sanity_check(functions)

        result = Encoder.dicts_from_sources(functions, verbose)
        return [_['functions'][0] for _ in result]

    @staticmethod
    def dicts_from_single_functions_parallel(functions:list, n_processes, verbose=False):
        buckets = Encoder.__split_buckets(functions, n_processes)

        with concurrent.futures.ProcessPoolExecutor() as e:
            futures = [e.submit(Encoder.dicts_from_single_functions, b, verbose) 
                        for b in buckets]
            
        result = []
        for future in futures: result += future.result()
        return result


    @staticmethod
    def dicts_from_files(files:list, verbose=False):
        srclist = []

        for file in files:
            with open(file) as f: src = f.read()
            srclist.append(src)
        
        return Encoder.dicts_from_sources(srclist, verbose)

    @staticmethod
    def dicts_from_files_parallel(files:list, n_processes=1, verbose=False):
        buckets = Encoder.__split_buckets(files, n_processes)

        with concurrent.futures.ProcessPoolExecutor() as e:
            futures = [e.submit(Encoder.dicts_from_files, b, verbose) 
                        for b in buckets]
            
        result = []
        for future in futures: result += future.result()
        return result


    @staticmethod
    def dicts_from_files_of_single_functions(files:list, verbose=False):
        srclist = []

        for file in files:
            with open(file) as f: src = f.read()
            srclist.append(src)
        
        return Encoder.dicts_from_single_functions(srclist, verbose)

    @staticmethod
    def dicts_from_files_of_single_functions_parallel(files:list, n_processes, verbose=False):
        srclist = []

        for file in files:
            with open(file) as f: src = f.read()
            srclist.append(src)
        
        return Encoder.dicts_from_single_functions_parallel(srclist, n_processes, verbose)


    @staticmethod
    def __split_buckets(list, n_processes):
        buckets = [[] for _ in range(n_processes)]

        for i, src in enumerate(list):
            index = i % n_processes
            buckets[index].append(src)

        return buckets

    @staticmethod
    def __function_sanity_check(function):
        """
        Check if function does not contain nested functions or classes.
        """
        return function.count('def ') == 1 and function.count('class ') == 0

    @staticmethod
    def __functions_sanity_check(functions):
        """
        Check if function does not contain nested functions or classes.
        """
        ret = []
        removed = 0
        for function in functions:
            if Encoder.__function_sanity_check(function):
                ret.append(function)
            else: removed += 1

        print(f'Sanity Check: removed {removed} functions.', flush=True)

        return ret