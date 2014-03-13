#!/usr/bin/python

from traits.api import HasTraits, Range, Instance, on_trait_change
from traitsui.api import View, Item, Group

from mayavi.core.api import PipelineBase
from mayavi.core.ui.api import MayaviScene, SceneEditor, MlabSceneModel

import numpy as np
import json, os
import nibabel

if not 'SUBJECTS_DIR' in os.environ:
    os.environ['SUBJECTS_DIR'] = '/usr/local/freesurfer/subjects'

base_path = os.environ['SUBJECTS_DIR'] + '/fsaverage'
pial_path = base_path + '/surf/lh.pial'
inflated_path = base_path + '/surf/lh.inflated'
sphere_path = base_path + '/surf/lh.sphere'
annot_path = base_path + '/label/lh.aparc.a2009s.annot'

class MyModel(HasTraits):
    t = Range(0., 1., 0.)

    scene = Instance(MlabSceneModel, ())
    plot = Instance(PipelineBase)

    pial, faces = nibabel.freesurfer.read_geometry(pial_path)
    inflated = nibabel.freesurfer.read_geometry(inflated_path)
    sphere = nibabel.freesurfer.read_geometry(sphere_path)
    ids, clut, labels = nibabel.freesurfer.read_annot(annot_path)

    @on_trait_change('t,scene.activated')
    def update_plot(self):
        a = 0.
        if self.t < 0.5:
            xyz0 = self.pial
            xyz1 = self.inflated[0]
            a = self.t / 0.5
        else:
            xyz0 = self.inflated[0]
            xyz1 = self.sphere[0]
            a = (self.t - 0.5) / 0.5
        x, y, z = ((1. - a) * xyz0 + a * xyz1).T
        
        if self.plot is None:
            # setup the mesh
            self.plot = self.scene.mlab.triangular_mesh(x, y, z, self.faces, scalars=self.ids)
            # setup the color LUT
            self.plot.module_manager.scalar_lut_manager.lut.table = self.clut[:,:4]
        else:
            # adjust
            self.plot.mlab_source.set(x=x, y=y, z=z)


    # The layout of the dialog created
    view = View(Item('scene', editor=SceneEditor(scene_class=MayaviScene),
                     height=600, width=600, show_label=False),
                Group(
                        '_', 't',
                     ),
                resizable=True,
                )


if __name__ == '__main__':
    my_model = MyModel()
    my_model.configure_traits()
