import os, gzip, json, zipfile, pathlib, uuid
from wacz.validate import Validation, OUTDATED_WACZ
from unwarcit.util import get_version, generate_datapackage, is_gz_file, write_out_file
from os.path import isfile, join, exists
from warcio.archiveiterator import ArchiveIterator
from warcio.checker import Checker
from wacz.util import WACZ_VERSION
from warcio.exceptions import ArchiveLoadFailed

# ============================================================================
class Unwarcit:
    def __init__(self, inputs, output):
        self.inputs = inputs
        self.output = output
        self.verbose = False # Hack because the imported library wants a self.verbose option
        self.unwarc = {}

    def unzip(self):
        """
        unzips the passed list of warcs and wacz files
        """
        valid_files = self.validate_passed_files(self.inputs)
        print("All files successfully validated")
        if valid_files == 1:
            return print("File failed to be validated")

        for key in self.inputs:
            self.unwarc[key] = {}
            self.unwarc = self.identify_file_formats(key, self.unwarc)
            current_file = self.unwarc[key]

            if current_file["format"] == "wacz":
                print(f"\nAnalyzing file {key}")
                warc_file = self.unzip_wacz(key, self.output)
                file_path = f"{self.output}/{key}/unpacked_wacz/archive/{warc_file}"

            else:
                warc_file = current_file
                print(f"\nAnalyzing file {key}")
                file_path = key

            self.unwrap_warc(key, file_path, self.unwarc)

            print("\nGenerating Datapackage.json file")
            datapackage = generate_datapackage(self.unwarc, key, self.output)
            datapackage_file = open(f"{self.output}/{key}/datapackage.json", "w")
            datapackage_file.write(datapackage)

    def identify_file_formats(self, file, unwarc):
        """
        Updates the self.unwarcit object file format and zipped status

        Looks at the passed file and creates it's entry in self.unwarcit with the format

        unwarc[file] = {
            "format": str,
            "file_is_zipped": boolean,
            "zipped_extension": str,
        }

        Parameters
        ----------
        file : str
            Description of arg1
        unwarc : dict
            Description of arg2

        Returns
        -------
        boolean
            Returns True

        """
        zip_format = file.split(".")[-1]
        format = file.split(".")[1]
        if zip_format == format:
            file_is_zipped = False
            zipped_extension = None
        else:
            file_is_zipped = True
            zipped_extension = zip_format
        unwarc[file] = {
            "format": format,
            "file_is_zipped": file_is_zipped,
            "zipped_extension": zipped_extension,
        }
        return unwarc

    def unzip_wacz(self, filepath, output):
        """
        unzips a wacz file allowing us to access original warc

        Parameters
        ----------
        filepath : str
            filepath to be opened and checked.
        output : str
            output folder to place unpacked wacz
        Returns
        -------
        str
            path of warc file to analyze

        """
        print(f"Unzipping wacz file {filepath}")
        with zipfile.ZipFile(filepath, "r") as zip_ref:
            pathlib.Path(f"{output}/{filepath}/unpacked_wacz/").mkdir(
                parents=True, exist_ok=True
            )
            zip_ref.extractall(f"{output}/{filepath}/unpacked_wacz/")

        warc_files = [
            f for f in os.listdir(f"{output}/{filepath}/unpacked_wacz/archive")
        ]
        if len(warc_files) != 1:
            print(
                "More than one warc detected in this wacz file, combining automatically"
            )
            # TODO: combine

        return warc_files[0]

    def unwrap_warc(self, file, file_path, unwarc):
        """
        reads a warc file and the conents of it's targets then writes them out to file and unwarc object

        Parameters
        ----------
        filepath : str
            filepath to be opened and checked.
        output : str
            output folder to place unpacked wacz
        Returns
        -------
        str
            path of warc file to analyze

        """
        print(f"Beginning to unwrap warc file {file}")
        is_gz = is_gz_file(file_path)
        if is_gz:
            opened_warc = gzip.open(file_path, "rb")
        else:
            opened_warc = open(file_path, "rb")
        with opened_warc as stream:
            unwarc[file]["found_files"] = []
            for record in ArchiveIterator(stream):
                if record.rec_type == "response":
                    name = record.rec_headers.get_header("WARC-Target-URI")
                    file_name = name.split("/")[-1].split("?")[0].split("@")[0]
                    content = record.content_stream().read()
                    content_length = len(content)
                    file_uuid = record.rec_headers.get_header("WARC-Record-ID")
                    file_uuid = file_uuid.split(":")[-1][0:-1]

                    if (content_length != 0):

                        if (file_name == '' and content_length > 0):
                            file_name = str(uuid.uuid4())
                            #print(f"\nA file with no name but some content has been detected, it will be stored as an 'unrecognized' type with the name {file_name}")

                        file_name = (file_name[-30:]) if len(file_name) > 250 else file_name

                        fetch_type = file_name.split(".")
                        if len(fetch_type) > 1:
                            fetch_type = fetch_type[-1]
                        elif file_name in ['css', 'html', 'jpg', 'js', 'json', 'php', 'png', 'svg']:
                            fetch_type = file_name
                        else:
                            fetch_type = 'unrecognized'


                        unwarc[file]["found_files"].append(
                            {
                                "url": name,
                                "file_name": file_name,
                                "detected_type": fetch_type,
                                "content": content,
                            }
                        )

                        write_out_file(self.output, file, fetch_type, file_name, content, file_uuid)

    def validate_wacz(self, file):
        """
        validate a passed wacz

        Parameters
        ----------
        file : str
            file to be opened and checked.

        Returns
        -------
        int
            1 if it fails 0 if its successful

        """
        print(f"Wacz file detected {file}, attempting validation")
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

    def validate_warc(self, file):
        """
        validate a passed warc

        Parameters
        ----------
        file : str
            file to be opened and checked.

        Returns
        -------
        int
            1 if it fails 0 if its successful

        """
        print(f"Warc file detected {file}, attempting validation")

        try:
            Checker.process_one(self, file)
        except ArchiveLoadFailed as e:
            logging.ingo(filename)
            print("  saw exception ArchiveLoadFailed: " + str(e).rstrip())
            print("  skipping rest of file")
            return 1
        return 0

    def validate_passed_files(self, files):
        """
        validates the passed list of files. Checks if they exist and then applies either warc or wacz validation.

        Parameters
        ----------
        files : list
            list of files to be opened and checked.

        Returns
        -------
        int
            1 if it fails 0 if its successful

        """
        all_files_are_valid = 0

        for file in files:
            file_exists = exists(file)
            print(f"file {file} exists {file_exists}")

            if file_exists:
                format = file.split(".")[1]
                if format == "wacz":
                    valid_wacz = self.validate_wacz(file)
                    all_files_are_valid = 1 if valid_wacz == 1 else 0
                elif format == "warc":
                    valid_warc = self.validate_warc(file)
                    all_files_are_valid = 1 if valid_warc == 1 else 0
            else:
                all_files_are_valid = 1
        return all_files_are_valid
