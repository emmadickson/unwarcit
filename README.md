UNWARCIT: WARC (and WACZ) Unzipping Library
========================================

Background
----------

This library provides a command line interface to unzip warc and wacz files.

Builds off of the `warcio library <https://github.com/webrecorder/warcio>` to read and validate warc files and the `py-wacz library <https://github.com/webrecorder/py-wacz>` to validate wacz files.

Both libraries are provided by
`Webrecorder <https://github.com/webrecorder/webrecorder>`

Setup
----------
Install by cloning the repo and then running: ``python3 setup.py install``

You can now run the tool like so:
`` unwarcit metro_capture2.wacz data.warc --output myfolder ``

You can pass a single file or a list of files, either warc or wacz, separated by spaces to unwarcit by placing them after the unwarcit command. 
`` unwarcit warcfile1.warc warcfile2.warc waczfile.wacz``

Configuration Options
----------

<details>
      <summary><b>Unwarcit currently accepts the following parameters:</b></summary>

```
      --help                                Show help                  [str]
      --version                             Show version number        [int]
      --output                              The folder to output the results to [str]
```
</details>
