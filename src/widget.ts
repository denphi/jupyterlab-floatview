// Copyright (c) Project Jupyter.
// Distributed under the terms of the Modified BSD License.

// TODO: import from @jupyter-widgets/jupyterlab-manager once Output is
// exported by the main module.
import {
    output
} from '@jupyter-widgets/jupyterlab-manager';
import {
    EXTENSION_SPEC_VERSION
} from './version';

export
    class FloatviewModel extends output.OutputModel {
    rendered: boolean;

    defaults() {
        return {
            ...super.defaults(),
            _model_name: FloatviewModel.model_name,
            _model_module: FloatviewModel.model_module,
            _model_module_version: FloatviewModel.model_module_version,
            _view_name: FloatviewModel.view_name,
            _view_module: FloatviewModel.view_module,
            _view_module_version: FloatviewModel.view_module_version,
            title: 'Floatview',
            mode: 'tab-after',
            active: false,
        };
    }

    initialize(attributes: any, options: any) {
        super.initialize(attributes, options);
        this.widget_manager.display_model(undefined, this, {});
    }

    static serializers: any = {
        ...output.OutputModel.serializers,
        // Add any extra serializers here
    }

    static model_name = 'FloatviewModel';
    static view_name = 'FloatviewView';
    static model_module = 'jupyterlab-floatview';
    static view_module = 'jupyterlab-floatview';
    static model_module_version = EXTENSION_SPEC_VERSION;
    static view_module_version = EXTENSION_SPEC_VERSION;
}
