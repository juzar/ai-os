import re
def extract_commands(text):
    patterns=[r"(kubectl[^\n]+)",r"(az[^\n]+)",r"(aws[^\n]+)"]
    cmds=[]
    for p in patterns:
        cmds+=re.findall(p,text)
    return cmds[:3]
