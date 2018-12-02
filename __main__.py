"""
Build xml file for wiki poll for House Votes.
"""

import json
import os
import shutil
import click
import jinja2
import uuid


def getFormResponse(): 
    var form = FormApp.openByUrl("https://docs.google.com/forms/d/e/1FAIpQLSdssq0eyVtpo4JnX-eDkLTqfqp1ulIZxNLie7bC5NzO1HQlfg/viewform?usp=sf_link")
    print(form)

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Print more output.')
# @click.argument('input_dir', required=True)
def main(verbose):
    """Templated xml generator."""
    try:

        form_data = getFormResponse();

        input_dir = os.path.dirname(os.path.abspath(__file__))
        template_dir = input_dir + '/templates'

        output_location = os.path.join(input_dir, 'out')

        if not os.path.isdir(output_location):
            os.mkdir(output_location)

        with open('config.json') as json_data:
            data = json.load(json_data)

        print(data)
        print(type(data))

        data = data[0]
        

        new_id = uuid.uuid1().int & (1<<64)-1
        print(new_id)
        data['context']['id'] = new_id
        print(data)
        print(type(data))

        template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_dir),
            autoescape=jinja2.select_autoescape(['html', 'xml']),
        )

        out_file = os.path.join(output_location, data['out_name'])

        template = template_env.get_template(data['template'])
        template_out = template.render(data['context'])

        with open(out_file, 'w') as file:
            file.write(template_out)

        if verbose:
            print('Rendered ' + page['template'] + ' -> ' + output_file)

    except jinja2.UndefinedError:
        print('Error_Jinja: Template tried to operate on Undefined')
        exit(1)

    except jinja2.TemplateNotFound:
        print('Error_Jinja: Template not found')
        exit(1)

    except jinja2.TemplateAssertionError:
        print('Error_Jinja: Assertion error')
        exit(1)

    except jinja2.TemplateSyntaxError:
        print('Error_Jinja: Template syntax error')
        exit(1)

    except jinja2.TemplateError:
        print('Error_Jinja: Template Error')
        exit(1)

    except json.JSONDecodeError:
        print('Error_JSON: Decoding error')
        exit(1)

    except FileNotFoundError:
        print('Error_FileNotFound: could not find file')
        exit(1)

if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    main()
