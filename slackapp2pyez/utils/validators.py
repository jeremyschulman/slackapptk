from typing import Union, Optional

import re
import ipaddress


_mac_char_re = re.compile(r'[0-9a-f]', re.I)


# TODO: add return format option.  Currently hardcodes to "2x:" format.
#
def validate_macaddr(
    macaddr
) -> Optional[str]:
    """
    Given `macaddr` string, determine that it is a valid MAC address
    containing only the specific supported alphanum values.

    Parameters
    ----------
    macaddr: str

    Returns
    -------
    None
        If `macaddr` is not a valid MAC address
    str
        If `macaddr` is a valid MAC address, and the returned
        format is "xx:xx:xx:xx:xx:xx"
    """
    char_list = _mac_char_re.findall(macaddr)
    if len(char_list) != 12:
        return None

    ch_i = iter(char_list)
    return ':'.join('%s%s' % (c, next(ch_i)) for c in ch_i)


def validate_ipaddress(
    ipaddr: str
) -> Optional[Union[ipaddress.IPv4Address, ipaddress.IPv6Address]]:
    """
    Given the IP address string, either return the enrobed ipaddress
    instance if valid, or None if not.

    Parameters
    ----------
    ipaddr: str

    Returns
    -------
    ipaddress.IPv4Address
        When `ipaddr` is a valid IPv4 address
    ipaddress.IPv6Address
        When `ipaddr` is a valid IPv6 address
    False
        Otherwise
    """
    try:
        return ipaddress.ip_address(ipaddr)

    except ValueError:
        return None
