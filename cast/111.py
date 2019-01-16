import re

line = "  rat.rid [*] <- [*] prs.origin  "
# line = " rat.rid [*] -> [*] prs.origin "

try:
    l, r = line.strip().split('<-')

    l, ln = re.split(r'\s', l.strip())
    lpath, lfield = l.split('.')
    ln = ln.strip('[]')

    rn, r = re.split(r'\s', r.strip())
    rpath, rfield = r.split('.')
    rn = rn.strip('[]')

    print(l, r)
except:
    # print ('wrong syntax: "{}"; expected: <parent>.<id_field> [<number>] <- [<number>] <scion>.<origin_field>'.format(line))

