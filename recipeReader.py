# pip install pyyaml
import yaml
import uuid


def parse_recipe_name(src, defaults):
    if src is not None and src != 'None':
        out = src
    else:
        out = defaults['recipe_name']
        print("Warning: no recipe name provided, using %s" % out)
    return out


def parse_oven_fan(src):
    if src is not None and src != 'None':
        if not src:
            out = 'Off'
        elif src.lower() == 'high':
            out = 'High'
        elif src.lower() == 'low':
            out = 'Low'
        elif src.lower() == 'off':
            out = 'Off'
        else:
            print("Warning: oven fan setting is invalid")
            out = src
    else:
        out = 'Off'
    return out


def parse_oven_temp(src_list):
    out = []
    if src_list is not None and src_list != 'None':
        if len(src_list) > 1:
            print("Warning: Multiple oven temperatures detected.")
        for src in src_list:
            this_oven_temp = dict()
            this_oven_temp['unit'] = ''
            this_oven_temp['amount'] = ''
            if src is not None:
                # Unit
                if 'unit' not in src:
                    print("Warning: no oven temp unit")
                elif src['unit'].lower() != 'c' and src['unit'].lower() != 'f':
                    print("Warning: oven temp unit is invalid")
                    this_oven_temp['unit'] = src['unit']
                else:
                    this_oven_temp['unit'] = src['unit'].upper()
                # Amount
                if 'amount' not in src:
                    print("Warning: no oven temp amount")
                else:
                    try:
                        this_oven_temp['amount'] = int(src['amount'])
                    except ValueError:
                        try:
                            this_oven_temp['amount'] = float(src['amount'])
                            print("Warning: oven temp amount is a float, not an int")
                        except ValueError:
                            this_oven_temp['amount'] = src['amount']
                            print("Warning: oven temp amount is not an int or float")
            out.append(this_oven_temp)
    return out


def parse_oven_time(src):
    out = ""
    if src is not None and src != 'None':
        out = src
    return out


def parse_yields(src, defaults):
    out = []
    if src is not None and src != 'None':
        for lst in src:
            for key, value in lst.items():
                # Amount
                try:
                    value = int(value)
                except ValueError:
                    try:
                        value = float(value)
                        print("Warning: yield amount is a float, not an int")
                    except ValueError:
                        print("Warning: yield amount is not an int or float")
                # Unit
                if key == "":
                    key = defaults['yields']['unit']
                    print("Warning: no yields unit, using %s" % key)
                out.append({key: value})
    return out


def parse_ingredients(src, defaults, expected_amount_size, substitution=False):
    out = []
    if src is not None and src != 'None':
        for ingredient_dict in src:
            ingredient_item = dict()
            for ingredient, details in ingredient_dict.items():

                # ingredient = Key of ingredient_item dict
                value = dict()

                # Amounts
                if 'amounts' in details:
                    amount_list = details.pop('amounts')
                    this_amount_list = []
                    if len(amount_list) != max(expected_amount_size, 1):
                        print("Warning: There is a mismatch between num of yields and num of measurements of "
                              "ingredients")
                    for item in amount_list:
                        amount_dict = dict()

                        # Unit
                        if 'unit' not in item:
                            amount_dict['unit'] = defaults['unit']
                            print("Warning: no unit provided for %s, using '%s'" % (ingredient, defaults['unit']))
                        else:
                            amount_dict['unit'] = item.pop('unit')

                        # Amount
                        if 'amount' not in item:
                            print("Warning: no amount provided for %s, using '%s'" % (ingredient, defaults['amount']))
                        else:
                            amount = item.pop('amount')
                            try:
                                amount_dict['amount'] = int(amount)
                            except ValueError:
                                try:
                                    amount_dict['amount'] = float(amount)
                                except ValueError:
                                    # This is fine, eg. 1 1/2 cups wouldn't be an int or float
                                    amount_dict['amount'] = amount
                        # Other
                        # There aren't meant to be other fields here, but it could contain notes.
                        # Eg. 3 cups sugar, packed tightly
                        for key, val in item.items():
                            print("Warning: Unknown value '%s' in amounts for '%s'" % (key, ingredient))
                            amount_dict[key] = val
                        this_amount_list.append(amount_dict)
                    value['amounts'] = this_amount_list
                else:
                    print("Warning: No amounts were provided for %s" % ingredient)

                # Processing
                if 'processing' in details:
                    value['processing'] = details.pop('processing')

                # Notes
                if 'notes' in details:
                    value['notes'] = details.pop('notes')

                # USDA Number
                if 'usda_num' in details:
                    value['usda_num'] = details.pop('usda_num')

                # Substitutions
                if not substitution:
                    if 'substitution' in details:
                        subs = details.pop('substitutions')
                        value['substitutions'] = parse_ingredients(subs, defaults, expected_amount_size, True)

                ingredient_item[ingredient] = value
            out.append(ingredient_item)
    else:
        if not substitution:
            print("Warning: no ingredients")
        else:
            print("Warning: no substitutions")
    return out


def parse_notes(src):
    out = []
    if src is not None and src != 'None':
        # No need to parse them, just replace the list if there are any
        out = src
    return out


def parse_recipe_uuid(src, defaults):
    out = defaults['recipe_uuid']
    if src is not None and src != 'None':
        out = src
    else:
        print("Warning: no UUID provided, using %s" % out)
    return out


def parse_source_book(src):
    out = dict()
    if src is not None and src != 'None':
        if 'authors' in src:
            out['authors'] = src.pop('authors')
        if 'title' in src:
            out['title'] = src.pop('title')
        if 'isbn' in src:
            out['isbn'] = src.pop('isbn')
        if 'notes' in src:
            out['notes'] = src.pop('notes')
        # If src not empty, the rest are x-fields
        for field, value in src.items():
            if field.startswith('x-'):
                out[field] = value
            else:
                print("Warning: Source book contained unknown field '%s', this is now 'x-%s'" % (field, field))
                out['x-%s' % field] = value
    return out


def parse_source_authors(src, defaults):
    out = defaults['source_authors']
    if src is not None and src != 'None':
        # No need to parse this
        out = src
    else:
        print("Warning: no source author provided, using %s" % out)
    return out


def parse_source_url(src, defaults):
    out = defaults['source_url']
    if src is not None and src != 'None':
        # No need to parse this
        out = src
    else:
        print("Warning: no source URL provided, using %s" % out)
    return out


def parse_steps(src):
    out = []
    if src is not None and src != 'None':
        for step in src:
            this_step = {}
            if 'step' not in step:
                print("Warning: a step is missing!")
            else:
                this_step['step'] = step['step']
            if 'haccp' in step:
                this_step['haccp'] = {}
                if 'control_point' in step['haccp'] and 'critical_control_point' in step['haccp']:
                    print("Warning: haccp contains both control point and critical control point")
                if 'control_point' in step['haccp']:
                    this_step['haccp']['control_point'] = step['haccp'].pop('control_point')
                if 'critical_control_point' in step['haccp']:
                    this_step['haccp']['critical_control_point'] = step['haccp'].pop('critical_control_point')
                if step['haccp']:
                    print("Warning: Haccp step contains a non-standard field(s)")
                    this_step['haccp'].update(step['haccp'])
            if 'notes' in step:
                this_step['notes'] = []
                for note in step['notes']:
                    this_step['notes'].append(note)
            out.append(this_step)
    else:
        print("Warning: no steps provided")
    return out


def parse_x_fields(src):
    # These fields are literally all the left over fields.
    out = dict()
    if src is not None and src != 'None':
        for field, value in src.items():
            if field.startswith('x-'):
                print("Warning: Recipe contained x-field '%s', it has been stored but not understood" % field)
                out[field] = value
            else:
                print("Warning: Recipe contained unknown field '%s', this is now 'x-%s'" % (field, field))
                out['x-%s' % field] = value
    return out


class Recipe:
    def __init__(self, config):

        self._dict = dict()

        # Convert to lowercase keys and save as cfg
        cfg = lower_key(config)

        # Default values
        defaults = dict()
        defaults['yields'] = {'unit': 'servings'}
        defaults['website'] = "example.recipes.com"
        defaults['software_package'] = "PyOpenRecipe"
        defaults['source_authors'] = ""
        defaults['uuid'] = str(uuid.uuid4())
        defaults['recipe_uuid'] = "%s-%s" % (defaults['software_package'], defaults['uuid'])
        defaults['recipe_name'] = 'untitled'
        defaults['source_url'] = "https://%s/%s/%s/" % (defaults['website'], defaults['recipe_name'], defaults['uuid'])
        defaults['unit'] = 'each'
        defaults['amount'] = 1

        # Recipe Name
        src = cfg.pop('recipe_name', None)
        self._dict['recipe_name'] = parse_recipe_name(src, defaults)

        defaults['source_url'] = "https://%s/%s/%s/" % (defaults['website'], defaults['uuid'],
                                                        self._dict['recipe_name'])

        # Oven Fan
        src = cfg.pop('oven_fan', None)
        self._dict['oven_fan'] = parse_oven_fan(src)

        # Oven Temp
        src = cfg.pop('oven_temp', None)
        self._dict['oven_temp'] = parse_oven_temp(src)

        # Oven Time
        src = cfg.pop('oven_time', None)
        self._dict['oven_time'] = parse_oven_time(src)

        # Yields
        src = cfg.pop('yields', None)
        self._dict['yields'] = parse_yields(src, defaults)

        # Ingredients
        src = cfg.pop('ingredients', None)
        self._dict['ingredients'] = parse_ingredients(src, defaults, len(self._dict['yields']))

        # Notes
        src = cfg.pop('notes', None)
        self._dict['notes'] = parse_notes(src)

        # Recipe UUID
        src = cfg.pop('recipe_uuid', None)
        self._dict['recipe_uuid'] = parse_recipe_uuid(src, defaults)

        # Source Book
        src = cfg.pop('source_book', None)
        self._dict['source_book'] = parse_source_book(src)

        # Source Authors
        src = cfg.pop('source_authors', None)
        self._dict['source_authors'] = parse_source_authors(src, defaults)

        # Source URL
        src = cfg.pop('source_url', None)
        self._dict['source_url'] = parse_source_url(src, defaults)

        # Steps
        src = cfg.pop('steps', None)
        self._dict['steps'] = parse_steps(src)

        # X-<field>
        self._dict['x'] = parse_x_fields(cfg)
        return

    def contents(self):
        return self._dict


######
# Lowers the keys of dictionaries recursively
# source: https://stackoverflow.com/questions/4223654/how-to-ensure-that-a-python-dict-keys-are-lowercase
# author: https://stackoverflow.com/users/186202/natim
######
def lower_key(in_dict):
    if type(in_dict) is dict:
        out_dict = {}
        for key, item in in_dict.items():
            out_dict[key.lower()] = lower_key(item)
        return out_dict
    elif type(in_dict) is list:
        return [lower_key(obj) for obj in in_dict]
    else:
        return in_dict


def load_file(filename):
    # Load the file using PyYAML
    with open(filename, 'r', encoding='utf8') as ymlfile:
        recipe = Recipe(yaml.safe_load(ymlfile))
    return recipe


def save_file(recipe, filename):
    # Save the file using PyYAML
    with open(filename, 'w', encoding='utf8') as outfile:
        yaml.dump(recipe.contents(), outfile, allow_unicode=True)
    return


if __name__ == "__main__":
    test = "samples/bananaBread.orf"
    test2 = "test/test2.orf"
    r = load_file(test)
    save_file(r, test2)
