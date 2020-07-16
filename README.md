# maya-resolver

Fetch and resolve Maya resources from a remote URL, skipping unnecessary downloads.

## Example Use Case

[This repository contains a large collection of resources](https://github.com/satire6/Spotify). It totals about 6 GB,
which is a considerable download (especially for fetching a single model).

We can use the `remote_resolve.py` script as follows to resolve just the resources for a scene like 
`bossbotHQ/CogGolfHub.mb` as follows:

1. Download the Maya file manually
2. Run

    ```
    mayapy path/to/remote_resolve.py CogGolfHub.mb \
        -s https://raw.githubusercontent.com/satire6/Spotify/master \
        -o CogGolfHub_Resolved.mb
    ```

    to download the missing resources. That's it! Note that a raw.githubusercontent.com URL is used to point directly
    to the files.

This reduces the download to a few megabytes.
