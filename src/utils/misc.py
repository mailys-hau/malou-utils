


def select_middle(inp, tg, pred, has_pred=True):
    if not isinstance(inp, list):
        return inp, tg, pred # Frame is already selected
    if len(inp) == 0: # Happend for "exported" TTE
        raise ValueError("This file is voxelless.")
    middle = int(len(inp) / 2)
    inp = inp[middle]
    tg = { k: v[middle] for k, v in tg.items() }
    if has_pred:
        pred = { k: v[middle] for k, v in pred.items() }
    return inp, tg, pred
