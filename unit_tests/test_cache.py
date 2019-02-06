from demo_data_gen import get_demo_data

import simple_imports
simple_imports.import_distributor()

from rtg.rtg_cache import RTGCache


if __name__ == '__main__':
    demo = RTGCache()

    demo.data = get_demo_data()  # Only for unit test

    print("Cache: Should be graphing flat lines.")

    demo.start()
