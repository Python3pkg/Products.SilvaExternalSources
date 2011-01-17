
(function($, CKEDITOR) {

    var fetchJSON = function(url, callback, object) {
        $.getJSON(
            $('#content-url').attr('href') + '/' + url,
            function(data) {
                callback.apply(object, [data]);
            }
        );
    };

    CKEDITOR.dialog.add('silvaexternalsource', function(editor) {
        return {
            title: 'Add a new External Source',
            minWidth: 350,
            minHeight: 130,
            contents: [
                { id: 'source',
                  elements: [
                      { type: 'select',
                        id: 'source_type',
                        label: 'Source to add',
                        required: true,
                        items: [],
                        setup: function(data) {
                            this.clear();
                            this.add('Select a source to add', '');
                            this.setValue('');
                            fetchJSON(
                                '++rest++Products.SilvaExternalSources.sources.available',
                                function(info) {
                                    var sources = info['sources'];

                                    this._.sources = sources;
                                    for (var i=0; i < sources.length; i++) {
                                        this.add(sources[i].title, sources[i].identifier);
                                    };
                                },
                                this);
                        },
                        onChange: function() {
                            var value = this.getValue();
                            var sources = this._.sources;
                            var source = null;
                            if (value)
                                // XXX Clear
                                return;

                            for (var i=0; i < sources.length; i++) {
                                if (sources[i].identifier == value) {
                                    source = sources[i];
                                };
                            };
                            if (!source)
                                // XXX Clear
                                return;
                        },
                        commit: function(data) {
                            var value = this.getValue();
                            var sources = this._.sources;

                            for (var i=0; i < sources.length; i++) {
                                if (sources[i].identifier == value) {
                                    data.source = sources[i];
                                };
                            };
                        }
                      },
                      { type: 'html',
                        id: 'source_params',
                        html: ''
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

