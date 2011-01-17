
CKEDITOR.plugins.add('silvaexternalsource', {
    requires: ['dialog'],
    init: function(editor) {
        editor.addCommand(
            'silvaexternalsource',
            new CKEDITOR.dialogCommand('silvaexternalsource'));
        editor.ui.addButton('SilvaExternalSource', {
            label: 'Add an External Source',
            command: 'silvaexternalsource',
            className: 'cke_button_hiddenfield'
        });
        // Dialog
        CKEDITOR.dialog.add('silvaexternalsource', this.path + 'dialogs/source.js');
        CKEDITOR.dialog.add('silvaexternalsourceparams', this.path + 'dialogs/source.js');
    }
});
