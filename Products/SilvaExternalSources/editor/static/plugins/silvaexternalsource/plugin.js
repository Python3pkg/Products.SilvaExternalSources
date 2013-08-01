
(function(CKEDITOR, $) {
    /**
     * Plugin for External Sources. External Sources inside the editor
     * are represented like this:
     *
     * <span class="inline-container silva-readonly-element">
     *    <div class="alignment external-source">
     *        <div class="external-source-preview" />
     *    </div>
     * </span>
     *
     * The outer span and inner div are added by the editor but should
     * be removed when saving. contenteditable is set to false on the
     * external source div.
     */

    CKEDITOR.plugins.silvaexternalsource = {
        isSourceWrapper: function(element) {
            // Return true if the element is an external source wrapper.
            if (element != null &&
                element.type == CKEDITOR.NODE_ELEMENT &&
                element.is('span') &&
                element.hasClass('inline-container')) {
                return true;
            }
            return false;
        },
        isSource: function(element) {
            // Return true if the element is a external source div.
            if (element != null &&
                element.type == CKEDITOR.NODE_ELEMENT &&
                element.is('div') &&
                element.hasClass('external-source')) {
                return true;
            };
            return false;
        },
        findSource: function(element) {
            // Return a source element if the given element is
            // instance a source.
            var initial = true,
                container = element;

            // Try to see if we are inside a source.
            while (container != null) {
                container = container.getAscendant('div', initial);
                if (API.isSource(container)) {
                    return container;
                };
                initial = false;
            };
            // Try to see if we have the wraper instead.
            container = element.getAscendant('span', true);
            if (API.isSourceWrapper(container)) {
                var children = container.getChildren(),
                    i, len, child;
                for (i=0, len=children.count(); i < len; i++) {
                    child = children.getItem(i);
                    if (API.isSource(child)) {
                        return child;
                    };
                };
            };
            return null;
        },
        getSelectedSource: function(editor, no_selection) {
            // Return the currently selected source.
            var selection = editor.getSelection(),
                source = null,
                wrapper = null,
                base = null;

            if (selection === null) {
                return null;
            };
            if (selection.getType() == CKEDITOR.SELECTION_ELEMENT) {
                base = selection.getSelectedElement();
            } else {
                base = selection.getStartElement();
            };
            source = API.findSource(base);
            if (source != null) {
                wrapper = source.getParent();
                if (!API.isSourceWrapper(wrapper)) {
                    wrapper = source;
                };
                // Select the wrapper if needed.
                if (!no_selection && wrapper.$ !== base.$) {
                    var range = new CKEDITOR.dom.range(editor.document);

                    range.selectNodeContents(wrapper);
                    range.select();
                };
                return source;
            };
            return null;
        },
        loadPreview: function($element, editor) {
            // element is a JQuery element. Editor a CKEditor one.
            var info = $element.attr('data-silva-settings');
            var $preview = $element.find('.external-source-preview');
            var content_url = $('#content-url').attr('href');
            var extra_info = [];

            // We load an existing code source. Add instance and text.
            if ($element.attr('data-silva-instance') != undefined) {
                extra_info.push({
                    'name': 'source_instance',
                    'value': $element.attr('data-silva-instance')
                });
                extra_info.push({
                    'name': 'source_text',
                    'value': editor.name
                });
            } else if ($element.attr('data-silva-name') != undefined) {
                // This is a new code source.
                extra_info.push({
                    'name': 'source_name',
                    'value': $element.attr('data-silva-name')
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
                    var is_dirty = editor.checkDirty();

                    if (!$preview.length) {
                        $element.empty(); //CKEditor adds an br in empty container.
                        $preview = $('<div class="external-source-preview"></div');
                        $preview.appendTo($element);
                        $preview.delegate('a', 'click', function(event) {
                            event.stopPropagation();
                            event.preventDefault();
                        });
                    };

                    $preview.html(html);

                    // If the document was unmodified, the fact to
                    // load the preview should not have modified it, reset the flag.
                    if (!is_dirty)
                        editor.resetDirty();
                }
            });
        }
    };

    var API = CKEDITOR.plugins.silvaexternalsource;

    CKEDITOR.externalSourceCommand = function(){};
    CKEDITOR.externalSourceCommand.prototype = {
        exec: function(editor) {
            var source = API.getSelectedSource(editor);

            if (source) {
                editor.openDialog('silvaexternalsourceedit');
            } else {
                editor.openDialog('silvaexternalsourcenew');
            };
        },
        canUndo: false,
        editorFocus : CKEDITOR.env.ie || CKEDITOR.env.webkit
    };

    CKEDITOR.removeExternalSourceCommand = function() {};
    CKEDITOR.removeExternalSourceCommand.prototype = {
        exec: function(editor) {
            var source = API.getSelectedSource(editor, true),
                wrapper;

            if (source !== null) {
                wrapper = source.getParent();
                if (API.isSourceWrapper(wrapper)) {
                    // Remove the source and the wrapper.
                    wrapper.remove();
                } else {
                    // Wrapper is missing (drag and drop abuse).
                    source.remove();
                };
            }
        },
        startDisabled: true
    };

    CKEDITOR.plugins.add('silvaexternalsource', {
        requires: ['dialog'],
        init: function(editor) {
            editor.addCommand(
                'silvaexternalsource',
                new CKEDITOR.externalSourceCommand());
            editor.addCommand(
                'silvaremoveexternalsource',
                new CKEDITOR.removeExternalSourceCommand());
            editor.ui.addButton('SilvaExternalSource', {
                label: 'Add an External Source',
                command: 'silvaexternalsource',
                className: 'cke_button_editdiv'
            });
            editor.ui.addButton('SilvaRemoveExternalSource', {
                label: 'Remove an External Source',
                command: 'silvaremoveexternalsource',
                className: 'cke_button_removediv'
            });
            editor.addCss(
                'span.inline-container {' +
                    'display: inline-block;' +
                    '}');
            editor.addCss(
                'div.external-source {' +
                    'margin: 5px 0;' +
                    'color: #444;' +
                    'background-color: #efefef;' +
                    'display: block;' +
                    'min-height: 20px;' +
                    'min-width: 20px;' +
                    '}');
            editor.addCss(
                'span.inline-container.float-left {' +
                    'float: left;' +
                    '}');
            editor.addCss(
                'span.inline-container.float-right {' +
                    'float: right;' +
                    '}');
            editor.addCss(
                'span.inline-container.align-left {' +
                    'text-align: left;' +
                    'display: block;' +
                    '}');
            editor.addCss(
                'span.inline-container.align-right {' +
                    'text-align: right;' +
                    'display: block;' +
                    '}');
            editor.addCss(
                'span.inline-container.align-center {' +
                    'text-align: center;' +
                    'display: block;' +
                    '}');

            // Events
            editor.on('contentDom', function(event) {
                // When a document is loaded, we load code sources previews
                var document = $(editor.document.getDocumentElement().$);

                document.find('.external-source').each(function () {
                    API.loadPreview($(this), editor);
                });
            });
            editor.on('selectionChange', function(event) {
                var element = API.getSelectedSource(editor),
                    command_edit = editor.getCommand('silvaexternalsource'),
                    command_remove = editor.getCommand('silvaremoveexternalsource');

                if (element !== null) {
                    command_edit.setState(CKEDITOR.TRISTATE_ON);
                    command_remove.setState(CKEDITOR.TRISTATE_OFF);
                } else {
                    command_edit.setState(CKEDITOR.TRISTATE_OFF);
                    command_remove.setState(CKEDITOR.TRISTATE_DISABLED);
                };
            });
            editor.on('doubleclick', function(event) {
                var element = API.getSelectedSource(editor);

                if (element !== null) {
                    event.data.dialog = 'silvaexternalsourceedit';
                };
            });
            editor.on('key', function(event) {
                if (editor.mode != 'wysiwyg')
                    return;

                var code = event.data.keyCode;
                // Improve the navigation before and after the code source with the arrows.
                if (code in {37:1, 38:1, 39:1, 40:1}) {
                    setTimeout(function() {
                        var source = API.getSelectedSource(editor, true),
                            parent = null;

                        if (source !== null) {
                            parent = source.getParent();
                            if (!API.isSourceWrapper(parent)) {
                                parent = source;
                            };
                            var target,
                                range,
                                selection = editor.getSelection(),
                                at_the_end;

                            if (code in {37:1, 38:1}) {
                                target = parent.getPrevious();
                                if (target === null) {
                                    target = editor.document.createElement('p');
                                    target.insertBefore(parent);
                                };
                                at_the_end = true;
                            } else {
                                target = parent.getNext();
                                if (target === null) {
                                    target = editor.document.createElement('p');
                                    target.insertAfter(parent);
                                };
                                at_the_end = false;
                            };
                            selection.unlock();
                            if (!CKEDITOR.env.ie) {
                                range = new CKEDITOR.dom.range(editor.document);
                                range.moveToPosition(target, at_the_end ?
                                                     CKEDITOR.POSITION_BEFORE_END:
                                                     CKEDITOR.POSITION_AFTER_START);
                                target.scrollIntoView();
                            } else {
                                range = editor.document.$.body.createTextRange();
                                range.moveToElementText(target.$);
                                range.collapse();
                                range.scrollIntoView();
                            };
                            selection.selectRanges([range]);
                            selection.lock();
                            editor.forceNextSelectionCheck();
                            editor.selectionChange(true);
                            setTimeout(function() {
                                selection.unlock();
                            }, 100);
                        };
                    }, 25);
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
                        className: 'cke_button_editdiv',
                        order: 1
                    },
                    silvaremoveexternalsource: {
                        label: 'Remove source',
                        command : 'silvaremoveexternalsource',
                        group : 'form',
                        className: 'cke_button_removediv',
                        order: 2
                    }
                });
            };
            if (editor.contextMenu) {
                editor.contextMenu.addListener(function(element, selection) {
                    if (API.findSource(element) !== null) {
                        return {
                            silvaexternalsource: CKEDITOR.TRISTATE_OFF,
                            silvaremoveexternalsource: CKEDITOR.TRISTATE_OFF
                        };
                    };
                    return null;
                });
            };

        },
        afterInit: function(editor) {
            // Input / Output transformations
            var dataProcessor = editor.dataProcessor,
                dataFilter = dataProcessor && dataProcessor.dataFilter,
                htmlFilter = dataProcessor && dataProcessor.htmlFilter;

            var remove = function(attributes, name) {
                // Remove an attribute from an object.
                if (attributes[name]) {
                    delete attributes[name];
                };
            };

            var is_source = function(element) {
                // Test if the given element is an external source div.
                return (element &&
                        element.name == 'div' &&
                        element.attributes['class'] != null &&
                        element.attributes['class'].match('^external-source'));
            };
            var is_wrapper = function(element) {
                // Test if the given element is a temporary container.
                return (element &&
                element.name == 'span' &&
                        element.attributes['class'] != null &&
                        element.attributes['class'].match('^inline-container'));
            };
            var is_preview = function(element) {
                // Test if the given element is a external source preview div.
                return (element &&
                        element.name == 'div' &&
                        element.attributes['class'] == 'external-source-preview');
            };


            if (dataFilter) {
                dataFilter.addRules({
                    elements: {
                        div: function(element) {
                            if (is_source(element)) {
                                var attributes = element.attributes,
                                    parent = element.parent,
                                    parse_alignment = /^external-source (.*)$/.exec(
                                        element.attributes['class']),
                                    alignment = 'default';

                                if (parse_alignment !== null) {
                                    alignment = parse_alignment[1];
                                };
                                attributes['contenteditable'] = 'false';
                                element.children = [];
                                if (!is_wrapper(parent)) {
                                    var container = new CKEDITOR.htmlParser.element(
                                        'span', {'class': 'inline-container ' + alignment});
                                    if (CKEDITOR.env.webkit) {
                                        // To help the selection in
                                        // Chrome we add a space before
                                        // and after each source.
                                        container.attributes['contenteditable'] = 'false';
                                        container.children = [
                                            new CKEDITOR.htmlParser.text('&#xfeff;'),
                                            element,
                                            new CKEDITOR.htmlParser.text('&#xfeff;')];
                                    } else {
                                        container.children = [element];
                                    };
                                    container.parent = parent;
                                    element.parent = container;
                                    return container;
                                };
                            };
                            return null;
                        }
                    }
                });
            };

            if (htmlFilter) {
                htmlFilter.addRules({
                    elements: {
                        span: function(element) {
                            var i, len;

                            if (is_wrapper(element)) {
                                for (i=0, len=element.children.length; i < len; i++) {
                                    if (is_source(element.children[i])) {
                                        return element.children[i];
                                    };
                                };
                                return false;
                            };
                            return null;
                        },
                        div: function(element) {
                            if (is_preview(element)) {
                                return false;
                            } else if (is_source(element)) {
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
})(CKEDITOR, jQuery);
