

(function($, CKEDITOR) {
    var API = CKEDITOR.plugins.silvaexternalsource,
        LIST_SOURCES_REST_URL = '++rest++Products.SilvaExternalSources.source.availables',
        VALIDATE_REST_URL = '++rest++Products.SilvaExternalSources.source.validate',
        PARAMETERS_REST_URL = '++rest++Products.SilvaExternalSources.source.parameters';

    /**
     * This object let you focus fields that cames from the template
     * rendered on the server containing External Source paramters.
     **/
    var ParameterFocusable = function(field, dialog) {
        var element = new CKEDITOR.dom.element(field),
            element_type = element.getAttribute('type'),
            field_type = (element_type && element_type.toLowerCase() == 'text') ? 'text': 'other';

        var focusable = {
            isParameter: function() {
                return true;
            },
            isFocusable: function() {
                return true;
            },
            tabIndex: 0,
            focusIndex: 0,
            keyboardFocusable: true,
            getInputElement: function() {
                return element;
            },
            type: field_type,
            focus: function() {
                return element.focus();
            },
            select: function() {
            }
        };
        element.on('focus', function() {
            dialog.currentFocusIndex = focusable.focusIndex;
        });
        return focusable;
    };

    var get_rest_url = function(url) {
        return $('#content-url').attr('href') + '/' + url;
    };

    /**
     * This function takes a jQuery element and a dialog and will
     * create declare to the dialog the focus order of any form field
     * found inside the element. start_index is the based index on
     * which to base the focus order.
     **/
    var update_focus_list = function($container, dialog, start_index) {
        var len, i = 0,
            parameter_list = [start_index, 0];

        // Step 1 remove any existing old parameters.
        for (i=0; i< dialog.focusList.length; i++) {
            if (dialog.focusList[i].isParameter && dialog.focusList[i].isParameter()) {
                dialog.focusList.splice(i, 1);
                i = i - 1;
            };
        };
        // Step 2 field parameters field and build a list of them.
        $container.find('input:visible,textarea:visible,select:visible').each(function() {
            parameter_list.push(ParameterFocusable(this, dialog));
        });
        // Step 3 merge the two focus lists on target.
        dialog.focusList.splice.apply(dialog.focusList, parameter_list);
        // Step 4 recompute focusIndex.
        for (i=0, len=dialog.focusList.length; i < len; i++) {
         	dialog.focusList[i].focusIndex = i;
        };
        if (dialog.focusList.length > 1) {
            dialog.focusList[0].focus();
        };
        dialog.currentFocusIndex = 0;
    };

    /**
     * Load inside the given jQuery element the parameters. This is
     * used inside the given dialog.
     **/
    var load_parameters = function($container, parameters, dialog, start_index) {
        // Fetch the parameters form.
        $container.html('<p>Fetching source parameters from server ...</p>');
        $.ajax({
            url: get_rest_url(PARAMETERS_REST_URL),
            data: parameters,
            dataType: 'json',
            type: 'POST',
            success: function(data) {
                var $form;

                dialog.parts.title.setText(
                    [$.trim(/^[^:]*/.exec(dialog.parts.title.getText())), ':', data.title].join(" "));
                $container.html(data.parameters);
                $form = $container.children('form');
                $form.trigger('load-smiform', {form: $form, container: $form});
                update_focus_list($form, dialog._, start_index);
            },
            error: function() {
                $container.html('');
                alert('An unexpected error happened on the server while ' +
                      'retrieving Code source parameters. ' +
                      'The Code Source might be buggy.');
            }
        });
    };

    var create_parameters_fields = function (parameters_identifier, start_index) {
        return [{
            type: 'html',
            id: 'source_options',
            html: '<div class="' + parameters_identifier + '"></div>',
            setup: function(data) {
                var $container = $('.' + parameters_identifier),
                    dialog = this.getDialog(),
                    parameters = [],
                    key, extra;

                this._.source = {};
                if (data.instance) {
                    var editor = dialog.getParentEditor();

                    this._.source['source_instance'] = data.instance;
                    this._.source['source_text'] = editor.name;
                } else if (data.name) {
                    this._.source['source_name'] = data.name;
                };
                if (data.parameters) {
                    extra = [{'name': 'source_inline', 'value':1}];
                    parameters = data.parameters;

                    for (key in this._.source) {
                        extra.push({'name': key, 'value': this._.source[key]});
                    };
                    parameters = parameters + '&' + $.param(extra);
                    load_parameters($container, parameters, dialog, start_index);
                } else if (data.instance) {

                    for (key in this._.source) {
                        parameters.push({'name': key, 'value': this._.source[key]});
                    };
                    load_parameters($container, $.param(this._.source), dialog, start_index);
                };
            },
            validate: function() {
                var $container = $('.' + parameters_identifier);
                var parameters = $container.find('form').serializeArray();
                var succeeded = true;

                // Add keys to identify the source.
                for (var key in this._.source) {
                    parameters.push({'name': key, 'value':this._.source[key]});
                };
                parameters.push({'name': 'source_inline', 'value': 1});

                $.ajax({
                    url: get_rest_url(VALIDATE_REST_URL),
                    data: parameters,
                    dataType: 'json',
                    type: 'POST',
                    async: false,
                    success: function(data) {
                        if (!data['success']) {
                            // First remove all previous errors.
                            $container.find('.external_source_error').remove();
                            // Create new error reporting.
                            for (var i=0; i < data['messages'].length; i++) {
                                var error = data['messages'][i];
                                var label = $container.find('label[for=' + error.identifier + ']');

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
                var $container = $('.' + parameters_identifier);

                data.parameters = $.param($container.find('form').serializeArray());
            }
        }, {
            type: 'select',
            id: 'source_align',
            label: 'Source alignement',
            required: true,
            items: [
                ['default', 'default'],
                ['align left', 'align-left'],
                ['align center', 'align-center'],
                ['align right', 'align-right'],
                ['float left', 'float-left'],
                ['float right', 'float-right']
            ],
            setup: function(data) {
                this.setValue(data.align || 'default');
            },
            commit: function(data) {
                data.align = this.getValue();
            }
        }];
    };

    CKEDITOR.dialog.add('silvaexternalsourcenew', function(editor) {
        return {
            title: 'Add a new External Source',
            minWidth: 600,
            minHeight: 400,
            contents: [{
                id: 'external_source_new_page',
                elements: [{
                    type: 'select',
                    id: 'source_type',
                    label: 'Source to add',
                    required: true,
                    items: [],
                    onChange: function(event) {
                        var dialog = this.getDialog();
                        var align_input = dialog.getContentElement(
                            'external_source_new_page', 'source_align').getElement();
                        var source_options = dialog.getContentElement(
                            'external_source_new_page', 'source_options');
                        var $container = $('.external_source_add');

                        if (event.data.value) {
                            if (source_options._.source) {
                                source_options._.source.source_name = event.data.value;
                            };
                            load_parameters($container, {'source_name': event.data.value}, dialog, 1);
                            align_input.show();
                        } else {
                            if (source_options._.source &&
                                source_options._.source.source_name) {
                                delete source_options._.source.source_name;
                            };
                            $container.html('');
                            align_input.hide();
                        }
                    },
                    setup: function(data) {
                        // Load the list of External Source from the server on setup.
                        var self = this;

                        this.clear();
                        this.add('Select a source to add', '');
                        this.setValue('');
                        $.getJSON(
                            get_rest_url(LIST_SOURCES_REST_URL),
                            function(sources) {
                                for (var i=0; i < sources.length; i++) {
                                    self.add(sources[i].title, sources[i].identifier);
                                };
                            });
                    },
                    validate: function() {
                        var checker = CKEDITOR.dialog.validate.notEmpty(
                            'You need to select a External Source to add !');

                        return checker.apply(this);
                    },
                    commit: function(data) {
                        data.name = this.getValue();
                    }
                }, {
                    type: 'vbox',
                    id: 'source_parameters',
                    children: create_parameters_fields('external_source_add', 1)
                }]
            }],
            onShow: function() {
                var data = {};
                this.setupContent(data);
                // Reset the title
                this.parts.title.setText($.trim(/^[^:]*/.exec(this.parts.title.getText())));
            },
            onOk: function() {
                var data = {};
                var editor = this.getParentEditor();

                this.commitContent(data);

                var selection = editor.getSelection();
                var ranges = selection.getRanges(true);

                var container = new CKEDITOR.dom.element('span');
                container.setAttributes({'class': 'inline-container ' + data.align});
                var source = new CKEDITOR.dom.element('div');
                var attributes = {};

                attributes['class'] = 'external-source ' + data.align;
                attributes['contenteditable'] = false;
                attributes['data-silva-name'] = data.name;
                attributes['data-silva-settings'] = data.parameters;
                source.setAttributes(attributes);
                container.append(source);
                ranges[0].insertNode(container);

                API.loadPreview($(source.$), editor);
            }
        };
    });

    CKEDITOR.dialog.add('silvaexternalsourceedit', function(editor) {
        return {
            title: 'External Source Settings',
            minWidth: 600,
            minHeight: 400,
            contents: [{
                id: 'external_source_edit_page',
                elements: create_parameters_fields('external_source_edit', 0)
            }],
            onShow: function() {
                var data = {};
                var editor = this.getParentEditor();
                var source = API.getSelectedSource(editor);
                var parse_alignment = /^external-source\s+([a-z-]+)\s*$/;
                var info_alignment = parse_alignment.exec(
                    source.getAttribute('class'));

                if (info_alignment != null) {
                    data.align = info_alignment[1];
                }
                data.name = source.getAttribute('data-silva-name');
                data.instance = source.getAttribute('data-silva-instance');
                if (source.hasAttribute('data-silva-settings')) {
                    data.parameters = source.getAttribute('data-silva-settings');
                };

                this.setupContent(data);
                // Reset the title
                this.parts.title.setText($.trim(/^[^:]*/.exec(this.parts.title.getText())));
            },
            onOk: function() {
                var data = {},
                    editor = this.getParentEditor(),
                    source = API.getSelectedSource(editor);

                this.commitContent(data);

                source.setAttribute('class', 'external-source ' + data.align);
                source.setAttribute('data-silva-settings', data.parameters);
                source.getParent().setAttribute('class', 'inline-container ' + data.align);

                API.loadPreview($(source.$), editor);
            }
        };
    });


})(jQuery, CKEDITOR);
