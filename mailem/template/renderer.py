from string import Template


class IRenderer(object):
    """ Base class for template renderer """

    def __init__(self, template, **kwargs):
        """ Init renderer with a template string

        :param template: Template string
        :type template: basestring
        :param kwargs: Additional arguments for the renderer
        :type kwargs: dict
        """
        raise NotImplementedError()

    def __call__(self, values):
        """ Render a template with the provided values.

        :param values: Values to render the template with.
        :type values: dict
        :returns: Rendered template
        :rtype: basestring
        """
        raise NotImplementedError()


class PythonTemplateRenderer(IRenderer):
    """ Simple Python Template renderer.

        Supported substitutions:

        * PythonTemplateRenderer('$what')(what=1)  #-> '1'
        * PythonTemplateRenderer('${what}')(what=1)  #-> '1'
        * PythonTemplateRenderer('$$what')(what=1)  #-> '$what'
    """

    def __init__(self, template):
        self.template = Template(template)

    def __call__(self, values):
        return self.template.substitute(values)


try:  # Only if jinja2 is available
    import jinja2

    class Jinja2TemplateRenderer(IRenderer):
        """ Jinja2 Template Renderer

        See <http://jinja.pocoo.org/docs/>.
        """

        def __init__(self, template, **kwargs):
            kwargs.setdefault('undefined', jinja2.StrictUndefined)
            kwargs.setdefault('keep_trailing_newline', True)
            env = jinja2.Environment(
                loader=jinja2.FunctionLoader(lambda name: template),
                **kwargs
            )
            self.template = env.get_template('x')

        def __call__(self, values):
            return self.template.render(values)

except ImportError:
    pass
