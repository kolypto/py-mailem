import os

from .template import Template


class TemplateRegistry(object):
    """ E-Mail template registry.

    Simply contains all your templates and allows to render these by name.
    Useful if you have multiple templates in your app and want to have them prepared.

    Initially, the registry is empty, and you add [`Template`](#template) objects one by one:

    ```python
    from mailem.template import Template, TemplateRegistry

    templates = TemplateRegistry()
    templates.add('signup', Template(
                'Congrats $user, you\'ve signed up!',
               'Welcome to our website!<br> -- $domain',
    ))
    templates.defaults(dict(domain='example.com'))  # set defaults on all templates
    ```

    Alternatively, you can use [`TemplateRegistry.from_directory()`](#templateregistryfrom_directory) to load templates
    from filesystem.

    Now, to render a template, you [`get()`](#templateregistryget) it by name:

    ```python
    msg = templates.get('signup')(['user@gmail.com'], dict(user='Honored User',))
    ```
    """

    @classmethod
    def from_directory(cls, path, **kwargs):
        """ Convenience method to construct a template registry
        with a directory where each template is in a subdirectory

        :param path: Path to templates
        :type path: str
        :param kwargs: Arguments to [Template.from_directory()](#templatefrom_directory), if required
        :rtype: mailem.template.registry.TemplateRegistry
        """
        registry = cls()
        for template_name in os.listdir(path):
            if template_name.startswith('.'):
                continue
            template_path = os.path.join(path, template_name)
            registry.add(template_name, Template.from_directory(template_path, **kwargs))
        return registry

    def __init__(self):
        self._templates = {}
        self._renderer = None
        self._defaults = {}

    def defaults(self, values):
        """ Set default values on all templates.

        New values will overwrite the previous.

        Can be called both before adding templates and after.

        :param values: Default template values
        :type values: dict
        """
        self._defaults.update(values)

        # Set it on all existing templates
        for t in self._templates.values():
            t.defaults(self._defaults)

        # Finish
        return self

    def set_renderer(self, renderer, **kwargs):
        """ Set renderer to be used with all templates.

        Can be called both before adding templates and after.

        :param renderer: Renderer class to use
        :type renderer: type
        :param kwargs: Additional arguments for the renderer
        :type kwargs: dict
        """
        assert self._renderer is None, 'Cannot re-assign a renderer'

        # Store
        self._renderer = renderer

        # Set it on all existing templates
        for t in self._templates.values():
            if not t._renderer:
                t.set_renderer(self._renderer, **kwargs)

        # Finish
        return self

    def add(self, name, template):
        """ Register a template

        :param template: Template object
        :type template: mailem.template.Template
        :returns: The added template (in case you want to set something on it)
        :rtype: mailem.template.Template
        """
        assert name not in self._templates, 'Duplicate template name'

        # Store
        self._templates[name] = template

        # Apply settings
        if self._renderer:
            template.set_renderer(self._renderer)
        template.defaults(self._defaults)

        # Finish
        return template

    def get(self, name):
        """ Get a Template by name

        :param name: Template name
        :type name: str
        :rtype: mailem.template.Template
        :raises KeyError: unknown template name
        """
        return self._templates[name]
