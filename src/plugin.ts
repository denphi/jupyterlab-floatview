// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.

import {
  JupyterLab, JupyterFrontEndPlugin
} from '@jupyterlab/application';

import {
    UUID
} from '@lumino/coreutils';

import {
  IJupyterWidgetRegistry
} from '@jupyter-widgets/base';

import {
  output
} from '@jupyter-widgets/jupyterlab-manager';

import {
    Message
} from '@lumino/messaging';

import {
  FloatviewModel
} from './widget';

import {
  EXTENSION_SPEC_VERSION
} from './version';

import {
  OutputArea
} from '@jupyterlab/outputarea';


import '../css/floatview.css';

const EXTENSION_ID = '@jupyter-widgets/jupyterlab-floatview';

const floatviewPlugin: JupyterFrontEndPlugin<void> = {
  id: EXTENSION_ID,
  requires: [IJupyterWidgetRegistry],
  activate: activateWidgetExtension,
  autoStart: true
};

export default floatviewPlugin;


class FloatViewOutputArea extends OutputArea{
  container: output.OutputView;
  processMessage(msg: Message) {
    switch (msg.type) {
    case 'close-request':
      this.container.model.set('uid', String('disposed'));
      this.container.model.save_changes();
      this.dispose();
      break;
    }
    super.processMessage(msg);

  }
  setContainer( container : output.OutputView ){
      this.container = container
  }

}

/**
 * Activate the widget extension.
 */
function activateWidgetExtension(app: JupyterLab, registry: IJupyterWidgetRegistry): void {
    let FloatviewView = class extends output.OutputView {
      model: FloatviewModel;

      render() {
        if (!this.model.rendered) {
          super.render();
          let w = new FloatViewOutputArea({
              rendermime: this.model.widget_manager.rendermime,
              contentFactory: OutputArea.defaultContentFactory,
              model: this.model.outputs
          });
          this._outputView = w;
          w.setContainer(this)
          w.addClass('jupyterlab-floatview');
          w.addClass('jp-LinkedOutputView');
          w.title.label = this.model.get('title');
          w.title.closable = true;
          w.id = UUID.uuid4();
          this.model.set('uid', String(w.id));
          this.model.save_changes();
          if (Object.keys(this.model.views).length > 1) {
            w.node.style.display = 'none';
            let key = Object.keys(this.model.views)[0];
            this.model.views[key].then((v: output.OutputView) => {
              v._outputView.activate();
            });
          } else {
            app.shell.add(w, 'main', { mode: this.model.get('mode') });
          }
        }
      }

    }

    registry.registerWidget({
      name: '@jupyter-widgets/jupyterlab-floatview',
      version: EXTENSION_SPEC_VERSION,
      exports: {
        FloatviewModel: FloatviewModel,
        FloatviewView: FloatviewView
      }
  });
}
