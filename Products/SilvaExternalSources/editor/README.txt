
REST API
--------

The REST API define the following URLs, on content:

- `Products.SilvaExternalSources.source.availables`

  Return a list of available sources as tuple of name and title.

- `Products.SilvaExternalSources.source.preview`

  Preview a source on the document called.

- `Products.SilvaExternalSources.source.parameters`

  Return a form letting editing the source parameters.

- `Products.SilvaExternalSources.source.validate`

  Validate a source parameters form submission.


The last three calls need data input:

- `source_instance` and `source_text`

  `source_instance` identifier a source instance in text attribute called
  `source_text` on the document.

OR

- `source_name`

  Source name.


To which you add:

- `source_inline`

  If present use request data instead of source data to work with
  (validate, render form, or render source).
