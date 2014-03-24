#!/usr/bin/env python

from traits.api import HasTraits, Range, Instance, on_trait_change
from traitsui.api import View, Item, Group

from mayavi.core.api import PipelineBase
from mayavi.core.ui.api import MayaviScene, SceneEditor, MlabSceneModel

import numpy as np
import json, os
import nibabel


class MyModel(HasTraits):
    t = Range(0., 1., 0.)

    scene = Instance(MlabSceneModel, ())
    plot = Instance(PipelineBase)

    def __init__(self, base_path, clut_name=None):
        super(HasTraits, self).__init__()
        self.base_path = base_path
        pial_path = base_path + '/surf/lh.pial'
        inflated_path = base_path + '/surf/lh.inflated'
        sphere_path = base_path + '/surf/lh.sphere'
        annot_path = base_path + '/label/lh.aparc.a2009s.annot'
        self.pial, self.faces = nibabel.freesurfer.read_geometry(pial_path)
        self.inflated = nibabel.freesurfer.read_geometry(inflated_path)
        self.sphere = nibabel.freesurfer.read_geometry(sphere_path)
        self.ids, self.clut, self.labels = nibabel.freesurfer.read_annot(annot_path)
        self.clut_name = clut_name

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
            if self.clut_name:
                self.plot = self.scene.mlab.triangular_mesh(x, y, z, self.faces, scalars=self.ids, colormap=self.clut_name)
            else:
                self.plot = self.scene.mlab.triangular_mesh(x, y, z, self.faces, scalars=self.ids)
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
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('subject', nargs='?', help='the subject\'s id', default='fsaverage')
    parser.add_argument('-c', '--clut', help='color LUT name', choices=['Accent', 'Blues', 'BrBG', 'BuGn', 'BuPu', 'Dark2', 'GnBu', 'Greens', 'Greys', 'OrRd', 'Oranges', 'PRGn', 'Paired', 'Pastel1', 'Pastel2', 'PiYG', 'PuBu', 'PuBuGn', 'PuOr', 'PuRd', 'Purples', 'RdBu', 'RdGy', 'RdPu', 'RdYlBu', 'RdYlGn', 'Reds', 'Set1', 'Set2', 'Set3', 'Spectral', 'YlGn', 'YlGnBu', 'YlOrBr', 'YlOrRd', 'autumn', 'binary', 'black-white', 'blue-red', 'bone', 'cool', 'copper', 'file', 'flag', 'gist_earth', 'gist_gray', 'gist_heat', 'gist_ncar', 'gist_rainbow', 'gist_stern', 'gist_yarg', 'gray', 'hot', 'hsv', 'jet', 'pink', 'prism', 'spectral', 'spring', 'summer', 'winter'])
    # use the suggested path in Freesurfer documentation
    parser.add_argument('-s', '--subjects_dir', help='path to subjects directory, overrides $SUBJECTS_DIR', 
                        default=os.environ['SUBJECTS_DIR'] if 'SUBJECTS_DIR' in os.environ else '/usr/local/freesurfer/subjects')
    args = parser.parse_args()

    base_path = '%s/%s' % (args.subjects_dir, args.subject)

    my_model = MyModel(base_path, args.clut)
    my_model.configure_traits()
