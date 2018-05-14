# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QWidget, QPushButton, QDialog, QTreeWidget,
                             QTreeWidgetItem, QVBoxLayout,
                             QHBoxLayout, QFrame, QLabel,
                             QApplication, QToolBar)

from PyQt5.QtCore import QSize, pyqtSlot
import OCC.Display.backend
back = OCC.Display.backend.load_backend()

from OCC.Display.qtDisplay import qtViewer3d
from OCC.AIS import AIS_Shaded,AIS_WireFrame, AIS_ColoredShape, \
    AIS_Axis, AIS_Line
from OCC.Aspect import Aspect_GDM_Lines, Aspect_GT_Rectangular
from OCC.Quantity import Quantity_NOC_BLACK as BLACK
from OCC.Geom import Geom_CylindricalSurface, Geom_Plane, Geom_Circle,\
     Geom_TrimmedCurve, Geom_Axis1Placement, Geom_Axis2Placement, Geom_Line
from OCC.gp import gp_Trsf, gp_Vec, gp_Ax3, gp_Dir, gp_Pnt, gp_Ax1
                             
from ..utils import layout

import qtawesome as qta

class OCCViewer(QWidget):

    
    def __init__(self,parent=None):
        
        super(OCCViewer,self).__init__(parent)
        
        self.canvas = qtViewer3d(self)
        self.toolbar = self.create_toolbar(self)
        
        self.layout = layout(self,
                             [self.toolbar,self.canvas],
                             self,
                             margin=0)
        
        self.canvas.InitDriver()
        self.show_edges()
        self.canvas._display.View.SetBgGradientColors(BLACK,BLACK,True)
        self.canvas._display.Repaint()
        
    def create_toolbar(self,parent):
        
        toolbar = QToolBar(parent)
        
        toolbar.addAction(qta.icon('fa.arrows-alt'),'Fit',self.fit)
        toolbar.addAction(qta.icon('fa.cube'),'Iso',self.iso_view)
        toolbar.addAction(qta.icon('fa.arrow-down'),'Top',self.top_view)
        toolbar.addAction(qta.icon('fa.arrow-up'),'Bottom',self.bottom_view)
        toolbar.addAction(qta.icon('fa.times-circle-o'),'Front',self.front_view)
        toolbar.addAction(qta.icon('fa.dot-circle-o'),'Back',self.back_view)
        toolbar.addAction(qta.icon('fa.arrow-right'),'Left',self.left_view)
        toolbar.addAction(qta.icon('fa.arrow-left'),'Right',self.right_view)
        toolbar.addAction(qta.icon('fa.square-o'),'Wireframe',self.wireframe_view)
        toolbar.addAction(qta.icon('fa.square'),'Shaded',self.shaded_view)
        
        toolbar.setIconSize(QSize(15,15))
        
        return toolbar
                
    def clear(self):
        
        self.displayed_shapes = []
        self.displayed_ais = []
        self.canvas._display.EraseAll()
        context = self._get_context()
        context.PurgeDisplay()
        context.RemoveAll()
        
    def _display(self,shape):
        
        ais = self.canvas._display.DisplayShape(shape)
        
        self.displayed_shapes.append(shape)
        self.displayed_ais.append(ais)
        
        self.canvas._display.Repaint()
        
    def show_edges(self,width=1.):
        
        context = self._get_context()
        drawer = context.DefaultDrawer().GetObject()
        drawer.SetFaceBoundaryDraw(True)
        
        face_boundry_aspect = drawer.FaceBoundaryAspect().GetObject()
        face_boundry_aspect.SetColor(BLACK)
        face_boundry_aspect.SetWidth(width)
        
    def hide_edges(self):
        
        context = self._get_context()
        drawer = context.DefaultDrawer().GetObject()
        drawer.SetFaceBoundaryDraw(False)
    
    def display(self,shape,name=''):
        
        ais = AIS_ColoredShape(shape)
        
        context = self._get_context()
        context.Display(ais.GetHandle())
        
        self.canvas._display.Repaint()
    
    @pyqtSlot(list)    
    def display_many(self,shapes):
        
        for shape in shapes:
            ais = AIS_ColoredShape(shape.wrapped)
        
        context = self._get_context()
        context.Display(ais.GetHandle())
        
        self.canvas._display.Repaint()
        
    def fit(self):
        
        self.canvas._display.FitAll()
        
    def iso_view(self):
        
        v = self._get_view()
        v.SetProj(1,1,1)
        v.SetTwist(0)
        
    def bottom_view(self):
        
        v = self._get_view()
        v.SetProj(0,0,1)
        v.SetTwist(0)
    
    def top_view(self):
        
        v = self._get_view()
        v.SetProj(0,0,-1)
        v.SetTwist(0)
    
    def front_view(self):
        
        v = self._get_view()
        v.SetProj(0,1,0)
        v.SetTwist(0)
    
    def back_view(self):
        
        v = self._get_view()
        v.SetProj(0,-1,0)
        v.SetTwist(0)
    
    def left_view(self):
        
        v = self._get_view()
        v.SetProj(1,0,0)
        v.SetTwist(0)
    
    def right_view(self):
        
        v = self._get_view()
        v.SetProj(-1,0,0)
        v.SetTwist(0)
        
    def shaded_view(self):
        
        c = self._get_context()
        c.SetDisplayMode(AIS_Shaded)
    
    def wireframe_view(self):
        
        c = self._get_context()
        c.SetDisplayMode(AIS_WireFrame)
        
    def show_grid(self,step=1,size=100):
        
        viewer = self._get_viewer()
        viewer.ActivateGrid(Aspect_GT_Rectangular,
                            Aspect_GDM_Lines)
        viewer.SetRectangularGridGraphicValues(size, size, 0)
        viewer.SetRectangularGridValues(0, 0, step, step, 0)
        
    def hide_grid(self):
        
        viewer = self._get_viewer()
        viewer.DeactivateGrid()
        
    def set_grid_orientation(self,center,dir1,dir2):
        
        orientation = gp_Ax3(gp_Pnt(*center), gp_Dir(*dir1), gp_Dir(*dir2))
        viewer = self._get_viewer()
        viewer.SetPrivilegedPlane(orientation)
        
    def show_axis(self,origin = (0,0,0), direction=(0,0,1)):
        
        ax_placement = Geom_Axis1Placement(gp_Ax1(gp_Pnt(*origin),
                                                  gp_Dir(*direction)))
        ax = AIS_Axis(ax_placement.GetHandle())
        self._display_ais(ax)
        
    def show_line(self,origin = (0,0,0), direction=(0,0,1)):
        
        line_placement = Geom_Line(gp_Ax1(gp_Pnt(*origin),
                                   gp_Dir(*direction)))
        line = AIS_Line(line_placement.GetHandle())
        self._display_ais(line)
        
    def _display_ais(self,ais):
        
        self._get_context().Display(ais.GetHandle())
 
        
    def _get_view(self):
        
        return self.canvas._display.GetView().GetObject()
        
    def _get_viewer(self):
        
        return self.canvas._display.GetViewer().GetObject()
            
    def _get_context(self):
        
        return self.canvas._display.GetContext().GetObject()

        
if __name__ == "__main__":
    
    
    import sys
    from OCC.BRepPrimAPI import BRepPrimAPI_MakeBox
    
    app = QApplication(sys.argv)
    viewer = OCCViewer()
    viewer.show_line()
    viewer.show()

    box = BRepPrimAPI_MakeBox(20,20,30)
    viewer.display(box.Shape())
    
    sys.exit(app.exec_())