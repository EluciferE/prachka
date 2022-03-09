def parseCell(cell: str) -> dict:
    answer = {}

    if "!" in cell:
        answer["listName"] = cell.split("!")[0]

        cell = cell.split("!")[1]

    answer["letter"] = ""
    for letter in cell:
        if letter.isdigit():
            break
        answer["letter"] += letter

    answer["number"] = ""
    for letter in cell:
        if letter.isdigit():
            answer["number"] += letter

    if not answer["letter"] or not answer["number"]:
        raise ValueError("Bad cell was given: " + cell)

    return answer
