import json

def load_json_snakes(fp):
    with open(fp, "r") as f:
        snake_list = json.load(f)

    return snake_list

def save_json_snakes(fp, snake_list):
    json_str = json.dumps(snake_list)

    with open(fp, 'w') as f:
        f.write(json_str)