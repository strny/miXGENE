import csv
import os
from templates.block_template import BLOCK_TEMPLATE, BLOCK_TEMPLATE_INDEX
from templates.main_page_template import MAIN_PAGE_MD, MAIN_PAGE_HTML
from templates.workflow_template import WORKFLOW_MD, WORKFLOW_HTML
from templates.category_template import CATEGORY_MD, CATEGORY_HTML
from templates.data_types_template import DATA_TYPES_MD, DATA_TYPES_HTML

__author__ = 'pavel'

DIR_BASE = 'doc'
WORKFLOW_DIR_BASE = DIR_BASE + '/workflow'
BLOCK_DIR_BASE = WORKFLOW_DIR_BASE + '/blocks'

class Page:
    @staticmethod
    def _create_dir(path):
        try:
            os.makedirs(path)
        except OSError:
            if not os.path.isdir(path):
                raise

    @staticmethod
    def generate_md_list(items):
        if items.strip():
            return '\n'.join(map(lambda (x): '* '+x.strip(), items.split(',')))
        else:
            return ""

    @staticmethod
    def _convert_name_to_fs_name(name):
        return name.strip().lower().replace(' ', '_').replace('/', '_')

    def generate(self):
        self.generate_md_file()
        self.generate_html_file()

    def generate_md_file(self):
        raise NotImplementedError()

    def generate_html_file(self):
        raise NotImplementedError()


class MainPage(Page):
    def __init__(self, workflow, data_types):
        self.workflow = workflow
        self.data_types = data_types

    def generate(self):
        self.generate_md_file()
        self.generate_html_file()
        self.data_types.generate()
        self.workflow.generate()


    def generate_md_file(self):
        block_dir = DIR_BASE
        self.__class__._create_dir(block_dir)
        with open(block_dir + '/' + 'index.md', "w") as out_file:
            out_file.write(MAIN_PAGE_MD)

    def generate_html_file(self):
        block_dir = DIR_BASE
        self.__class__._create_dir(block_dir)
        with open(block_dir + '/' + 'index.html', "w") as out_file:
            out_file.write(MAIN_PAGE_HTML)


class Workflow(Page):
    def generate(self):
        self.generate_md_file()
        self.generate_html_file()
        for cat in self.categories:
            cat.generate()

    def generate_html_file(self):
        self.__class__._create_dir(WORKFLOW_DIR_BASE)
        with open(WORKFLOW_DIR_BASE + '/' + 'index.html', "w") as out_file:
            out_file.write(WORKFLOW_HTML)

    def generate_md_file(self):
        self.__class__._create_dir(WORKFLOW_DIR_BASE)
        with open(WORKFLOW_DIR_BASE + '/' + 'index.md', "w") as out_file:
            out_file.write(self.workflow_template())

    def workflow_template(self):
        block_vars = {'block_categories': self.generate_md_list(','.join(["[{0}]({1})".format(cat.name, cat.url()) for cat in self.categories]))
                      }
        return WORKFLOW_MD.format(**block_vars)

    def __init__(self, categories):
        self.categories = categories

    # def add_category(self, cat):
    #     self.categories.append(cat)


class Category(Page):
    def __init__(self, name, description):
        self.name = name.strip()
        self.description = description
        self.blocks = []

    def add_block(self, block):
        self.blocks.append(block)

    def generate(self):
        self.generate_md_file()
        self.generate_html_file()
        for block in self.blocks:
            block.generate()

    def url(self):
        return 'blocks/' + self._convert_name_to_fs_name(self.name) + '/index.html'

    def generate_md_file(self):
        block_dir = BLOCK_DIR_BASE + '/' + self._convert_name_to_fs_name(self.name)
        self.__class__._create_dir(block_dir)
        with open(block_dir + '/' + 'index.md', "w") as out_file:
            out_file.write(self.category_template())

    def generate_html_file(self):
        block_dir = BLOCK_DIR_BASE + '/' + self._convert_name_to_fs_name(self.name)
        self.__class__._create_dir(block_dir)
        with open(block_dir + '/' + 'index.html', "w") as out_file:
            out_file.write(CATEGORY_HTML)

    def category_template(self):
        block_vars = {'block_list': self.generate_md_list(','.join(["[{0}]({1})".format(block.name, block.url()) for block in self.blocks])),
                      'description': self.description,
                      'category_name': self.name}
        return CATEGORY_MD.format(**block_vars)

    @staticmethod
    def create_categories_from_csv(csv_file):
        with open(csv_file, 'rb') as csvfile:
            cats = []
            cats_file = csv.DictReader(csvfile, delimiter=',', quotechar='"')
            for row in cats_file:
                cats.append(Category(row['Name'], row['Description']))
        return cats


class Block(Page):

    def __init__(self, name, category, description, inputs, parameters, outputs):
        self.name = name.strip()
        self.category = category.strip()
        self.description = description
        self.inputs = inputs
        self.parameters = parameters
        self.outputs = outputs
        self.data_types = {}

    def set_data_types(self, data_types):
        self.data_types = data_types

    @staticmethod
    def create_blocks_from_csv(csv_file):
        with open(csv_file, 'rb') as csvfile:
            blocks = []
            blocks_file = csv.DictReader(csvfile, delimiter=',', quotechar='"')
            for row in blocks_file:
                blocks.append(Block(row['Current name'], row['Future category'], row['Description'], row['Inputs'], row['Parameters'], row['Outputs']))
        return blocks

    def url(self):
        return self._convert_name_to_fs_name(self.name)+ '.html'

    def generate_md_file(self):
        block_dir = BLOCK_DIR_BASE + '/' + self._convert_name_to_fs_name(self.category)
        self.__class__._create_dir(block_dir)
        with open(block_dir + '/' + self._convert_name_to_fs_name(self.name) + '.md', "w") as out_file:
            out_file.write(self.block_template())

    def generate_html_file(self):
        block_dir = BLOCK_DIR_BASE + '/' + self._convert_name_to_fs_name(self.category)
        self.__class__._create_dir(block_dir)
        with open(block_dir + '/' + self._convert_name_to_fs_name(self.name) + '.html', "w") as out_file:
            out_file.write(self.block_index_template())

    def block_index_template(self):
        block_vars = {'mdfile': self._convert_name_to_fs_name(self.name) + '.md'}
        return BLOCK_TEMPLATE_INDEX.format(**block_vars)

    def add_data_types_url(self, input_str):
        for key in self.data_types.types.keys():
            input_str = input_str.replace(key, "[{0}]({1})".format(key, "../../../data_types.html#{0}".format(key.lower())))
        return input_str

    def block_template(self):
        block_vars = {'block_name': self.name,
                      'block_category': self.category,
                      'description': self.description,
                      'inputs': self.generate_md_list(self.add_data_types_url(self.inputs)),
                      'parameters': self.generate_md_list(self.parameters),
                      'outputs': self.generate_md_list(self.add_data_types_url(self.outputs))}
        return BLOCK_TEMPLATE.format(**block_vars)


class DataTypes(Page):
    @staticmethod
    def create_from_csv(csv_file):
        with open(csv_file, 'rb') as csvfile:
            types = {}
            blocks_file = csv.DictReader(csvfile, delimiter=',', quotechar='"')
            for row in blocks_file:
                types[row['Name']] = row['Description']
        return DataTypes(types)

    def __init__(self, types):
        self.types = types

    def generate_md_file(self):
        block_dir = DIR_BASE
        self.__class__._create_dir(block_dir)
        with open(block_dir + '/' + 'data_types.md', "w") as out_file:
            out_file.write(self.data_type_template())

    def generate_html_file(self):
        block_dir = DIR_BASE
        self.__class__._create_dir(block_dir)
        with open(block_dir + '/' + 'data_types.html', "w") as out_file:
            out_file.write(DATA_TYPES_HTML)

    def data_type_template(self):
        s = ''
        for key, val in self.types.items():
            s = s + "# {0}".format(key) + "\n" + val + "\n"
        block_vars = {'data_types': s}
        return DATA_TYPES_MD.format(**block_vars)

os.system("rm -rf doc")

blocks = Block.create_blocks_from_csv('blocks.csv')
categories = Category.create_categories_from_csv('categories.csv')
data_types = DataTypes.create_from_csv('data_types.csv')
for c in categories:
    for b in blocks:
        if b.category == c.name:
            b.set_data_types(data_types)
            c.add_block(b)

mp = MainPage(Workflow(categories), data_types)
mp.generate()
# generate_blocks_index(blocks)
