
(function($, CKEDITOR) {

    var fetchJSON = function(url, callback, object) {
        $.getJSON(
            $('#content-url').attr('href') + '/' + url,
            function(data) {
                callback.apply(object, [data]);
            }
        );
    };

    var API = CKEDITOR.plugins.silvaexternalsource;
    var LIST_SOURCES_REST_URL = '++rest++Products.SilvaExternalSources.source.availables';
    var VALIDATE_REST_URL = '/++rest++Products.SilvaExternalSources.source.validate';
    var PARAMETERS_REST_URL = '/++rest++Products.SilvaExternalSources.source.parameters';

    CKEDITOR.dialog.add('silvaexternalsource', function(editor) {
        return {
            title: 'Add a new External Source',
            minWidth: 600,
            minHeight: 400,
            contents: [
                { id: 'source',
                  elements: [
                      { type: 'select',
                        id: 'source_type',
                        label: 'Source to add',
                        required: true,
                        items: [],
                        setup: function(data) {
                            // Load the list of External Source from the server on setup.
                            this.clear();
                            this.add('Select a source to add', '');
                            this.setValue('');
                            fetchJSON(
                                LIST_SOURCES_REST_URL,
                                function(info) {
                                    var sources = info['sources'];
                                    var data = this._.silva = {};

                                    data.document = info['document'];
                                    data.sources = sources;
                                    data.source = null;
                                    for (var i=0; i < sources.length; i++) {
                                        this.add(sources[i].title, sources[i].identifier);
                                    };
                                },
                                this);
                        },
                        onChange: function() {
                            // If the selected External Source changed, that
                            // something is selected, fetch its parameters form
                            // into #external_source_container.
                            var data = this._.silva || {};

                            if (!data.sources)
                                return;

                            var container = $('.external_source_container');
                            var value = this.getValue();
                            var source = null;

                            var clean_container = function () {
                                data.source = null;
                                container.html('');
                            };

                            if (!value) {
                                clean_container();
                                return;
                            };
                            for (var i=0; i < data.sources.length; i++) {
                                if (data.sources[i].identifier == value) {
                                    source = data.sources[i];
                                };
                            };
                            if (!source) {
                                clean_container();
                                return;
                            };
                            // The currently selected source is saved in the field.
                            data.source = source;
                            // Fetch the parameters form.
                            $.ajax({
                                url: source.url + PARAMETERS_REST_URL,
                                data: {'document': data.document},
                                dataType: 'html',
                                success: function(html) {
                                    container.html(html);
                                },
                                error: function() {
                                    alert('An unexpected error happened on the server while ' +
                                          'retrieving Code source parameters. ' +
                                          'The Code Source might be buggy.');
                                    clean_container();
                                }
                            });
                        },
                        // Validation happens in source_parameters
                        commit: function(data) {
                            data.source = this._.silva.source;
                        }
                      },
                      { type: 'html',
                        id: 'source_params',
                        html: '<div class="external_source_container"></div>',
                        validate: function() {
                            var dialog = this.getDialog();
                            var data = dialog.getContentElement(
                                'source', 'source_type')._.silva || {};

                            if (!data.sources) {
                                // The whole popup is not even ready yet.
                                return false;
                            }
                            if (!data.source) {
                                alert('No External Source is selected!');
                                return false;
                            };

                            var parameters = $('.external_source_fields').serializeArray();
                            var succeeded = true;

                            parameters.push({name: 'document', value: data.document});
                            console.log(parameters);
                            $.ajax({
                                url: data.source.url + VALIDATE_REST_URL,
                                data: parameters,
                                dataType: 'json',
                                type: 'POST',
                                async: false,
                                success: function(data) {
                                    if (!data['success']) {
                                        // First remove all previous errors.
                                        $('.external_source_error').remove();
                                        // Create new error reporting.
                                        for (var i=0; i < data['messages'].length; i++) {
                                            var error = data['messages'][i];
                                            var label = $('label[for=' + error.identifier + ']');

                                            $('<span class="external_source_error">' +
                                              error.message + '</span>').insertAfter(label);
                                        };
                                        alert('Some parameters did not validate properly. '+
                                              'Please correct the errors.');
                                        succeeded = false;
                                    }
                                },
                                error: function() {
                                    alert('An unexpected error happened on the server ' +
                                          'while validating the code source. The code source ' +
                                          'might be buggy.');
                                    succeeded = false;
                                }
                            });
                            return succeeded;
                        },
                        commit: function(data) {
                            data.parameters = $('.external_source_fields').serializeArray();
                        }
                      }
                  ]
                }
            ],
            onShow: function() {
                var data = {};

                this.setupContent(data);
            },
            onOk: function() {
                var data = {};
                var editor = this.getParentEditor();

                this.commitContent(data);
                console.log(data);

                var selection = editor.getSelection();
                var ranges = selection.getRanges(true);

                var div = new CKEDITOR.dom.element('div');
                var div_attributes = {};

                div_attributes['class'] = 'external-source';
                div_attributes['contenteditable'] = false;
                div_attributes['data-silva-settings'] = $.param(data.parameters);
                div.unselectable();
                div.setAttributes(div_attributes);
                ranges[0].insertNode(div);
                selection.selectElement(div);

                API.loadPreview($(div.$));
            }
        };
    });

    CKEDITOR.dialog.add('silvaexternalsourceparams', function(editor) {
        return {
            title: 'Edit External Source Parameters',
            minWidth: 350,
            minHeight: 130,
            contents: [
                { id: 'source',
                  elements: [
                  ]
                }
            ]
        };
    });


})(jQuery, CKEDITOR);

