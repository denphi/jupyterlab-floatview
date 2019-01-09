// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.

import {
  JupyterLab, JupyterLabPlugin
} from '@jupyterlab/application';

import {
    UUID
} from '@phosphor/coreutils';

import {
  IJupyterWidgetRegistry
 } from '@jupyter-widgets/base';

// TODO: import from @jupyter-widgets/jupyterlab-manager once Output is
// exported by the main module.
import {
   OutputView
} from '@jupyter-widgets/jupyterlab-manager/lib/output';

import {
    Message
} from '@phosphor/messaging';

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

const floatviewPlugin: JupyterLabPlugin<void> = {
  id: EXTENSION_ID,
  requires: [IJupyterWidgetRegistry],
  activate: activateWidgetExtension,
  autoStart: true
};

export default floatviewPlugin;


class FloatViewOutputArea extends OutputArea{
  container: OutputView;
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
  setContainer( container : OutputView ){
      this.container = container      
  }
  
}
            
/**
 * Activate the widget extension.
 */
function activateWidgetExtension(app: JupyterLab, registry: IJupyterWidgetRegistry): void {
    let FloatviewView = class extends OutputView {
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
            this.model.views[key].then((v: OutputView) => {
              v._outputView.activate();
            });
          } else {
            app.shell.addToMainArea(w, { mode: this.model.get('mode') });
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
