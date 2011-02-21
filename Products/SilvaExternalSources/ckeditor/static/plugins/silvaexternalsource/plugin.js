
(function(CKEDITOR) {

    CKEDITOR.plugins.silvaexternalsource = {
        isSource: function(element) {
            if (element != null &&
                element.is('div') &&
                element.hasClass('external-source')) {
                return true;
            };
            return false;
        },
        isInsideASource: function(element) {
            var first_try = true;

            while (element != null) {
                element = element.getAscendant('div', first_try);
                if (CKEDITOR.plugins.silvaexternalsource.isSource(element)) {
                    return element;
                }
                first_try = false;
            };
            return null;
        },
        getSelectedSource: function(editor, select_base_element) {
            var selection = editor.getSelection();
            var element = null;
            var base = null;

            if (selection.getType() == CKEDITOR.SELECTION_ELEMENT) {
                base = selection.getSelectedElement();
            } else {
                base = selection.getStartElement();
            };
            element = CKEDITOR.plugins.silvaexternalsource.isInsideASource(base);
            if (element != null) {
                if (base.$ != element.$ && select_base_element) {
                    selection.selectElement(element);
                }
                return element;
            }
            return null;
        },
        loadPreview: function(element, editor) {
            // element is a JQuery element. Editor a CKEditor one.
            var info = element.attr('data-silva-settings');
            var preview = element.find('.external-source-preview');
            var content_url = $('#content-url').attr('href');
            var extra_info = [];

            // We load an existing code source. Add instance and text.
            if (element.attr('data-silva-instance') != undefined) {
                extra_info.push({
                    'name': 'source_instance',
                    'value': element.attr('data-silva-instance')
                });
                extra_info.push({
                    'name': 'source_text',
                    'value': editor.name
                });
            } else if (element.attr('data-silva-name') != undefined) {
                // This is a new code source.
                extra_info.push({
                    'name': 'source_name',
                    'value': element.attr('data-silva-name')
                });
            };
            // Merge all preview information together.
            if (info == undefined) {
                info = $.param(extra_info);
            } else {
                // Those are inline changed options.
                extra_info.push({'name': 'source_inline', 'value': 1});
                info += '&' + $.param(extra_info);
            };

            $.ajax({
                url: content_url + '/++rest++Products.SilvaExternalSources.source.preview',
                data: info,
                type: 'POST',
                success: function(html) {
                    if (!preview.length) {
                        element.empty(); //CKEditor adds an br in empty container.
                        preview = $('<div class="external-source-preview"></div');
                        preview.appendTo(element);
                    };

                    preview.html(html);
                }
            });
        }
    };

    var API = CKEDITOR.plugins.silvaexternalsource;

    CKEDITOR.externalSourceCommand = function(){};
    CKEDITOR.externalSourceCommand.prototype = {
        exec: function(editor) {
            var source = API.getSelectedSource(editor, true);

            if (source) {
                editor.openDialog('silvaexternalsourceedit');
            } else {
                editor.openDialog('silvaexternalsourcenew');
            };
        },
        canUndo: false,
        editorFocus : CKEDITOR.env.ie || CKEDITOR.env.webkit
    };

    CKEDITOR.plugins.add('silvaexternalsource', {
        requires: ['dialog'],
        init: function(editor) {
            editor.addCommand(
                'silvaexternalsource',
                new CKEDITOR.externalSourceCommand());
            editor.ui.addButton('SilvaExternalSource', {
                label: 'Add an External Source',
                command: 'silvaexternalsource',
                className: 'cke_button_hiddenfield'
            });
            editor.addCss(
                'div.external-source {' +
                    'padding: 1px;' +
                    'color: #444;' +
                    'background-color: #EEE8AA;' +
                    'display: inline-block;' +
                    '}');
            editor.addCss(
                'div.source-float-left {' +
                    'float: left;' +
                    '}');
            editor.addCss(
                'div.source-float-right {' +
                    'float: right;' +
                    '}');
            editor.addCss(
                'div.source-left {' +
                    'text-align: left;' +
                    'display: block;' +
                    '}');
            editor.addCss(
                'div.source-right {' +
                    'text-align: right;' +
                    'display: block;' +
                    '}');
            editor.addCss(
                'div.source-center {' +
                    'text-align: center;' +
                    'display: block;' +
                    '}');

            // Events
            editor.on('contentDom', function(event) {
                // When a document is loaded, we load code sources previews
                var document = $(editor.document.getDocumentElement().$);

                document.find('.external-source').each(function (index, element) {
                    API.loadPreview($(element), editor);
                });
            });
            editor.on('selectionChange', function(event) {
                var element = API.getSelectedSource(editor, true);
                var command = editor.getCommand('silvaexternalsource');

                if (element != null) {
                    command.setState(CKEDITOR.TRISTATE_ON);
                } else {
                    command.setState(CKEDITOR.TRISTATE_OFF);
                };
            });
            editor.on('doubleclick', function(event){
                var element = API.getSelectedSource(editor, true);

                if (element != null) {
                    event.data.dialog = 'silvaexternalsourceedit';
                };
            });

            // Dialog
            CKEDITOR.dialog.add('silvaexternalsourcenew', this.path + 'dialogs/source.js');
            CKEDITOR.dialog.add('silvaexternalsourceedit', this.path + 'dialogs/source.js');

            // Menu
            if (editor.addMenuItems) {
                editor.addMenuItems({
                    silvaexternalsource: {
                        label: 'Source settings',
                        command : 'silvaexternalsource',
                        group : 'form',
                        className: 'cke_button_hiddenfield',
                        order: 1
                    }
                });
            };
            if (editor.contextMenu) {
                editor.contextMenu.addListener(function(element, selection) {
                    if (API.isInsideASource(element)) {
                        return {
                            silvaexternalsource: CKEDITOR.TRISTATE_OFF
                        };
                    };
                    return null;
                });
            };

        },
        afterInit: function(editor) {
            // Input / Output transformations
            var dataProcessor = editor.dataProcessor;
            var dataFilter = dataProcessor && dataProcessor.dataFilter;
            var htmlFilter = dataProcessor && dataProcessor.htmlFilter;

            var remove = function(attributes, name) {
                // Remove an attribute from an object.
                if (attributes[name]) {
                    delete attributes[name];
                };
            };
            var is_source_div = function(element) {
                // Test if the given element is an image div.
                return (element &&
                        element.name == 'div' &&
                        element.attributes['class'] != null &&
                        element.attributes['class'].match('external-source'));
            };
            var is_preview_div = function(element) {
                // Test if the given element is an image div.
                return (element &&
                        element.name == 'div' &&
                        element.attributes['class'] == 'external-source-preview');
            };


            if (dataFilter) {
                dataFilter.addRules({
                    elements: {
                        div: function(element) {
                            if (is_source_div(element)) {
                                var attributes = element.attributes;

                                attributes['contenteditable'] = 'false';
                                element.children = [];
                            };
                            return null;
                        }
                    }
                });
            };

            if (htmlFilter) {
                htmlFilter.addRules({
                    elements: {
                        div: function(element) {
                            if (is_preview_div(element)) {
                                return false;
                            } else if (is_source_div(element)) {
                                var attributes = element.attributes;

                                remove(attributes, 'contenteditable');
                                remove(attributes, 'style');
                                return null;
                            };
                            return null;
                        }
                    }
                    });
            };
        }

    });
})(CKEDITOR);