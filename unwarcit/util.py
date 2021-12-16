import pathlib, datetime, json, pkg_resources
from wacz.util import WACZ_VERSION, support_hash_file, now


def get_version():
    """
    Returns the current version of unwarcit

    Parameters
    ----------
    None

    Returns
    -------
    str
        version of unwarcit being used

    """
    return "%(prog)s " + pkg_resources.get_distribution("unwarcit").version


def generate_datapackage(unwarc, key, output, hash_type="md5"):
    """
    Generates a datapackage.json file

    The datapackage is Frictionless compliant

    Parameters
    ----------
    unwarc : dict
        object storing info about the files we're recovering
    key : str
        the key for the file we need to process in the unwarc dict
    output : str
        The output folder for the files
    hash_type : The hash algorithm used to hash the file contents

    Returns
    -------
    json
        content of data_package file

    """
    unwarc_record = unwarc[key]
    package_dict = {}

    package_dict["profile"] = "data-package"
    package_dict["resources"] = []
    for i in range(0, len(unwarc_record["found_files"])):
        file = unwarc_record["found_files"][i]
        package_dict["resources"].append({})
        package_dict["resources"][i]["name"] = file["file_name"].lower()
        package_dict["resources"][i]["detected_type"] = file["detected_type"]
        package_dict["resources"][i][
            "stored_path"
        ] = f"{output}/{key}/{file['detected_type']}/{file['file_name']}"
        package_dict["resources"][i]["url"] = file["url"]
        content = file["content"]
        package_dict["resources"][i]["hash"] = support_hash_file(hash_type, content)
        package_dict["resources"][i]["bytes"] = len(content)

        package_dict["created"] = datetime.datetime.utcnow().strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )

        package_dict["wacz_version"] = WACZ_VERSION

        package_dict["software"] = "unwarcit " + get_version()

    return json.dumps(package_dict, indent=2)


def is_gz_file(filepath):
    """
    Identifies if a file is .gz zipped or not

    Parameters
    ----------
    filepath : str
        filepath to be opened and checked.

    Returns
    -------
    boolean
        True if the file is .gz zipped, otherwise False

    """
    with open(filepath, "rb") as test_f:
        return test_f.read(2) == b"\x1f\x8b"


def write_out_file(output, original_file, file_path, file_name, content):
    """
    Writes the passed information to the given file path
    Parameters
    ----------
    key : str
        The name of the original warc or wacz file
    file_path : str
        The output folder where we will place the file
    file_name : str
        individual file name
    content : str
        content to be written to file

    Returns
    -------
    None

    """
    path = f"{output}/{original_file}/downloaded_files/{file_path}"
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)
    f = open(f"{path}/{file_name}", "wb")
    f.write(content)
    return
