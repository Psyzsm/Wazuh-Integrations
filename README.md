# Wazuh Discord Integration
Just a Github repo containing the two discord-custom and discord-custom.py files I personally went through and audited to slot into my setup to be released with my [setup blog](blog.psyzsm.com/central-watchtower/)

### Changelog
| File | Change | Reason |
|--|--|--|
| shell | `unset WAZUH_PATH` | Prevents a pre-set env var from redirecting the Python binary path |
| shell | Removed `[ -z "${WAZUH_PATH}" ]` guards | Redundant after the unset; always derive path from script location |
| shell | Quoted all variable expansions | Prevents word splitting / glob expansion on paths with spaces |
| shell | `cd ... && pwd` instead of `cd ...; pwd` | `&&` ensures `pwd` doesn't silently run after a failed `cd` |
| shell | Added `*)` default case → `exit 1` | Fails loudly from an unexpected directory instead of misbehaving silently |
| shell | Added `[ ! -f "${PYTHON_SCRIPT}" ]` check | Clear error if the `.py` file is missing, instead of a cryptic Python traceback |
| shell | `exec` before final invocation | Replaces the shell process with Python rather than forking a child — leaner on 1-core VPS nodes |
| python | Fixed shebang `#!` (was `#`) | Without `!` it's just a comment; OS won't invoke Python at all |
| python | Removed `HTTPBasicAuth` import + unused `user` var | Dead code left from the Slack-derived original |
| python | Added `len(sys.argv) < 4` guard | Prevents `IndexError` crash on missing args |
| python | Wrapped file read in `try/except` | Handles disk errors and malformed JSON gracefully |
| python | `alert_json.get("agent", {}).get("name", "unknown")` | Prevents `KeyError` on non-standard alert schemas |
| python | Wrapped payload build in `try/except KeyError` |  Catches any other missing rule fields at build time |
| python | Color as `int` not `str` | Discord's API silently drops string-typed embed colors |
| python | `timeout=10` on `requests.post` | Prevents the integration from hanging and blocking Wazuh's queue |
| python | `r.raise_for_status()` | Surfaces Discord 4xx/5xx errors instead of swallowing them |
| python | Granular `except` blocks per error type | Specific, actionable messages land in `/var/ossec/logs/integrations.log` |
| python | `sys.exit(1)` on all failure paths | Lets Wazuh's integratord correctly flag/log integration failures |

## Original Repo and Guide I followed:
[Guide](https://maikroservice.com/how-to-connect-wazuh-and-discord-a-step-by-step-guide) and [Repo](https://github.com/maikroservice/wazuh-integrations)


## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
