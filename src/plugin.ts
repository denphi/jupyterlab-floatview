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
  FloatviewModel
} from './widget';

import {
  EXTENSION_SPEC_VERSION
} from './version';

import '../css/floatview.css';

const EXTENSION_ID = 'jupyterlab-floatview';

const floatviewPlugin: JupyterLabPlugin<void> = {
  id: EXTENSION_ID,
  requires: [IJupyterWidgetRegistry],
  activate: activateWidgetExtension,
  autoStart: true
};

export default floatviewPlugin;


/**
 * Activate the widget extension.
 */
function activateWidgetExtension(app: JupyterLab, registry: IJupyterWidgetRegistry): void {
    let FloatviewView = class extends OutputView {
      model: FloatviewModel;

      render() {
        if (!this.model.rendered) {
          super.render();
          let w = this._outputView;
          w.addClass('jupyterlab-floatview');
          w.addClass('jp-LinkedOutputView');
          w.title.label = this.model.get('title');
          w.title.closable = true;
          /*w.title.closable = true;
          app.shell['_rightHandler'].sideBar.tabCloseRequested.connect((sender : any, tab : any) => {
              tab.title.owner.dispose();
          });*/
		  app.shell['_dockPanel']
          w.id = UUID.uuid4();
          if (Object.keys(this.model.views).length > 1) {
            w.node.style.display = 'none';
            let key = Object.keys(this.model.views)[0];
            this.model.views[key].then((v: OutputView) => {
              v._outputView.activate();
            });
          } else {
            app.shell.addToMainArea(w, { mode: this.model.get('mode') });
            /*app.shell.expandRight();*/
          }
        }
      }
    }

    registry.registerWidget({
      name: 'jupyterlab-floatview',
      version: EXTENSION_SPEC_VERSION,
      exports: {
        FloatviewModel: FloatviewModel,
        FloatviewView: FloatviewView
      }
  });
}
