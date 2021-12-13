from argparse import ArgumentParser, RawTextHelpFormatter
import sys
from os.path import exists
from wacz.validate import Validation, OUTDATED_WACZ
from wacz.util import WACZ_VERSION

def get_version():
    import pkg_resources
    return '%(prog)s ' + pkg_resources.get_distribution('warcit').version



# ============================================================================
def main(args=None):
    if sys.version_info < (2, 7):
        print('Sorry, warcit requires python >= 2.7, you are running {0}'.format(sys.version.split(' ')[0]))
        return 1

    parser = ArgumentParser(description='Unzip Warc and Wacz files')

    parser.add_argument('-V', '--version', action='version', version=get_version())

    parser.add_argument('inputs', nargs='+',
                    help='''Paths of directories and/or files to be included in
                            the WARC file.''')

    parser.add_argument('--format',
                        help='''Select format''',
                        choices=['warc', 'wacz'])

    arguments = parser.parse_args(args=args)


    return UNWARCIT(arguments.inputs, arguments.format).run()


def validate_wacz(file):
    validate = Validation(file)
    version = validate.version
    validation_tests = []

    if version == OUTDATED_WACZ:
        print("Validation Succeeded the passed Wacz is outdate but valid")
        return 0

    elif version == WACZ_VERSION:
        validation_tests += [
            validate.check_required_contents,
            validate.frictionless_validate,
            validate.check_file_paths,
            validate.check_file_hashes,
        ]
    else:
        print("Validation Failed the passed Wacz is invalid")
        return 1

    for func in validation_tests:
        success = func()
        if success is False:
            print("Validation Failed the passed Wacz is invalid")
            return 1

    print("Validation Succeeded the passed Wacz is valid")
    return 0

# ============================================================================
class UNWARCIT():
    def __init__(self, inputs, format):
        self.inputs = inputs
        self.format = format

    def run(self):
        print('int the run')
        print(self.inputs)
        print(self.format)

        self.validate_passed_file(self.inputs)


    def validate_passed_file(self, files):
        for file in files:
            file_exists = exists(file)
            print(file_exists)
            if (file_exists):
                t = validate_wacz(file)
                print(t)

# ============================================================================
if __name__ == "__main__":
    res = main()
    sys.exit(res)
