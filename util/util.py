def convert_to_grid_format(items, tabs):
    items_dict = {}
    for tab in tabs:
        rows = []
        curr_row = []
        for idx,item in enumerate(items):
            if idx != 0 and idx % 3 == 0:
                rows.append(curr_row)
                curr_row = []
            curr_row.append(item)
        if len(curr_row) > 0:
            rows.append(curr_row)
        items_dict[tab] = rows
    return items_dict