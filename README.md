# Darryl's CardScanner
This script is **quite basic** and may need further optimization for efficiency and accuracy, especially in handling large files or different file formats. Also, running this script on a system could consume significant resources, depending on the amount of data to be scanned.

# Considerations
* **Privacy and Security**: Scanning for credit card data can have legal and privacy implications. Ensure you have the proper authorization and comply with relevant laws and regulations.  
* **Performance**: This script may take a significant amount of time and resources to run, especially on large file systems.  
* **False Positives/Negatives**: The script uses basic pattern matching which might not be accurate for all cases. It may produce false positives or miss some valid card numbers.  
* **File Types**: This script is basic and reads files as plain text. It doesn't handle binary files or specific formats like PDFs or Word documents.

You should test this script thoroughly in a controlled environment before considering using it in a production scenario.

# Usage
`python3 darryls_cardscan.py`

# Known issues

## Memory Consumption with Large Files
The script may consume a significant amount of memory when processing large files. If the script terminates unexpectedly and you see a `Killed` message at the end of the run, this may indicate that the system ran out of memory.

To confirm this, you can check the system logs for out-of-memory (OOM) messages. Here are examples of what these messages might look like in your logs:
```
/var/log/syslog:Dec 19 11:14:37 ubuntu-20-04LTS kernel: [5254542.740910] Out of memory: Killed process 2190495 (python3) total-vm:674264kB, anon-rss:302008kB, file-rss:2320kB, shmem-rss:0kB, UID:1000 pgtables:664kB oom_score_adj:0
/var/log/syslog:Dec 19 11:14:37 ubuntu-20-04LTS kernel: [5254542.749772] oom_reaper: reaped process 2190495 (python3), now anon-rss:0kB, file-rss:0kB, shmem-rss:0kB
```
If you encounter this issue, consider:
a) Running the script on a system with more available memory.
b) Added `-chunk` to the command line. Do note that this will lower accuracy because reading in 1MB chunks can split a credit card number across two chunks. This may also increase the time it takes to run.

# LEGAL DISCLAIMER
The provided script ("Software") is offered "AS IS" without any warranty of any kind, either expressed or implied, including, but not limited to, the implied warranties of merchantability, fitness for a particular purpose, and non-infringement.

The user assumes the entire risk as to the quality and performance of the Software. In no event shall the author or contributors be liable for any consequential, incidental, direct, indirect, special, punitive, or other damages whatsoever (including, without limitation, damages for loss of business profits, business interruption, loss of business information, or other pecuniary loss) arising out of the use or inability to use the Software, even if advised of the possibility of such damages.

This Software is intended for use only by individuals or organizations with the appropriate expertise and understanding of the potential risks, including but not limited to data privacy, legal compliance, and system performance impacts. The user is responsible for ensuring that their use of the Software complies with all applicable laws and regulations.

By using the Software, the user acknowledges and agrees to conduct due diligence, assume full responsibility for any risks, and exercise caution in the use and implementation of the Software. The user must also ensure that they have the necessary rights and permissions to scan and analyze the data targeted by the Software.

This disclaimer shall be construed and governed in accordance with the laws of the jurisdiction in which the Software is used. Any legal action or proceeding relating to your access to, or use of, the Software shall be instituted in a state or federal court in the relevant jurisdiction, and you hereby agree to submit to the jurisdiction of such courts.

