# coding: utf-8

def split_parameters(parameters):
    # Avoid split("/") because of escaped slashes
    new_parameters = []
    start = 0
    backslash = False
    cur = ""
    for j, c in enumerate(parameters):
        if j < start:
            pass
        elif c == "\\":
            backslash = True
        elif c == "/":
            if backslash:
                cur += c
                backslash = False
            else:
                new_parameters.append(cur)
                cur = ""
                start = j + 1
        else:
            if backslash:             # let's not forget the \
                cur += "\\"
            cur += c
            backslash = False

    new_parameters.append(parameters[start:])
    return new_parameters