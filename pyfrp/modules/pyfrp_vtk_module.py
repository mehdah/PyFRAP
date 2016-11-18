#=====================================================================================================================================
#Copyright
#=====================================================================================================================================

#Copyright (C) 2014 Alexander Blaessle, Patrick Mueller and the Friedrich Miescher Laboratory of the Max Planck Society
#This software is distributed under the terms of the GNU General Public License.

#This file is part of PyFRAP.

#PyFRAP is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

#===========================================================================================================================================================================
#Module Description
#===========================================================================================================================================================================

"""VTK module for PyFRAP toolbox. 

Contains functions that allow drawing/plotting via VTK. For more information about VTK, go to
www.vtk.org and http://www.vtk.org/Wiki/VTK/Examples/Python .

"""

#===========================================================================================================================================================================
#Improting necessary modules
#===========================================================================================================================================================================

#numpy
import numpy as np
import scipy.interpolate

#Plotting
import vtk
import matplotlib

#Misc
import sys
import os

#PyFRAP
import pyfrp_img_module
from pyfrp_term_module import *
from pyfrp.modules import pyfrp_idx_module

#===========================================================================================================================================================================
#Module Functions
#===========================================================================================================================================================================

def makeVTKCanvas(offScreen=False,bkgd=[1,1,1],renderer=None):
	
	"""Creates a vtk renderer and includes it into a renderer window.
	
	.. warning:: ``offScreen=True`` is still in development. 
	
	If ``renderer`` is given, will just create the render Window and interactor around
	it.
	
	Keyword Args:
		offScreen (bool): Don't show Window.
		bkgd (list): Background color of renderer in normed RGB values.
		renderer (vtk.vtkRenderer): Renderer.
		
	Returns:
		tuple: Tuple containing:
		
			* renderer (vtk.renderer): Renderer.
			* renderWindow (vtk.renderWindow): Render Window.
			* renderWindowInteractor (vtk.renderWindowInteractor): Render Window Interactor.
				
	"""
	
	if renderer==None:
		renderer = vtk.vtkRenderer()
	renderWindow = vtk.vtkRenderWindow()
	
	# This seems to be the key to have a renderer without displaying. However it returns floating 
	# Errors.
	if offScreen:
		renderWindow.OffScreenRenderingOn() 
	
	renderWindow.AddRenderer(renderer)
	renderer.SetBackground(bkgd[0], bkgd[1], bkgd[2]) 
	
	renderWindowInteractor = vtk.vtkRenderWindowInteractor()
	renderWindowInteractor.SetRenderWindow(renderWindow)

	return renderer, renderWindow, renderWindowInteractor

def renderVTK(renderer):
	
	"""Renders everything contained in renderWindow
	and starts Interactor.
	
	Args:
		renderer (vtk.vtkRenderer): A renderer.
		
	Returns:
		vtk.vtkRenderer: Renderer.
	
	"""

	if renderer.GetRenderWindow()==None:
		renderer,renderWindow,renderWindowInteractor=makeVTKCanvas(renderer=renderer)
	
	renderer.GetRenderWindow().Render()
	renderer.GetRenderWindow().GetInteractor().Start()
	
	return renderer
	
def drawVTKPoint(p,asSphere=True,color=[0,0,0],size=10,renderer=None):
	
	"""Draws point into renderer.

	If ``renderer=None``, will create actor but not add it to renderer.
	
	Args:
		p (numpy.ndarray): Position of point.
		
	Keyword Args:
		color (list): Color of sphere in normed RGB values.
		size (float): Size of vertex/radius of sphere.
		asSphere (bool): Draw point as sphere.
		renderer (vtk.vtkRenderer): Renderer to draw in.
		
	Returns:
		vtk.vtkActor: VTK actor.
	
	"""
	
	if asSphere:
		return drawVTKSphere(p,size,color=color,renderer=renderer)
	else:
		return drawVTKVertex(p,size,color=color,renderer=renderer)
	
def drawVTKVertex(p,color=[0,0,0],size=20,renderer=None):	
	
	"""Draws vtk vertex given its position into renderer.
	
	If ``renderer=None``, will create actor but not add it to renderer.
	
	Args:
		p (numpy.ndarray): Position of vertex.
		
	Keyword Args:
		color (list): Color of sphere in normed RGB values.
		size (float): Size of vertex.
		renderer (vtk.vtkRenderer): Renderer to draw in.
		
	Returns:
		vtk.vtkSphereSource: VTK actor.
	
	"""
	
	# Create the topology of the point (a vertex)
	vertices = vtk.vtkCellArray()
	
	#Add points
	points = vtk.vtkPoints()
	id = points.InsertNextPoint(p)
	vertices.InsertNextCell(1)
	vertices.InsertCellPoint(id)

	# Create a polydata object
	point = vtk.vtkPolyData()
	
	# Set the points and vertices we created as the geometry and topology of the polydata
	point.SetPoints(points)
	point.SetVerts(vertices)
	
	# Visualize
	actor = getVTKActor(color)
	actor.GetProperty().SetPointSize(size)
	actor.SetMapper(getVTKPolyDataMapper(point))
	
	return actor

def drawVTKSphere(center,radius,color=[0,0,0],renderer=None):
	
	"""Draws vtk source sphere with given center and radius into renderer.
	
	If ``renderer=None``, will create actor but not add it to renderer.
	
	Args:
		center (numpy.ndarray): Center of sphere.
		radius (float): Radius of sphere.
	
	Keyword Args:
		color (list): Color of sphere in normed RGB values.
		renderer (vtk.vtkRenderer): Renderer to draw in.
		
	Returns:
		vtk.vtkActor: VTK actor.
	
	"""
	
	sphere=getVTKSphere(center,radius)
	
	actor=getVTKActor(color)
	actor.SetMapper(getVTKPolyDataMapper(getVTKOutput(sphere)))
	
	if renderer!=None:
		renderer.AddActor(actor)
		
	return actor

def drawVTKLine(p1,p2,color=[0,0,0],renderer=None):
	
	"""Draws VTK line object going from point 1 to point 2 into renderer.
	
	If ``renderer=None``, will create actor but not add it to renderer.
	
	Args:
		p1 (numpy.ndarray): Coordinate of point 1.
		p2 (numpy.ndarray): Coordinate of point 2.
	
	Keyword Args:
		color (list): Color of sphere in normed RGB values.
		renderer (vtk.vtkRenderer): Renderer to draw in.
		
	Returns:
		vtk.vtkActor: VTK actor.
	
	"""
	
	line=getVTKLine(p1,p2)
	
	actor=getVTKActor(color)
	actor.SetMapper(getVTKPolyDataMapper(getVTKOutput(line)))
	
	if renderer!=None:
		renderer.AddActor(actor)
		
	return actor

def getVTKLine(p1,p2):
	
	"""Returns VTK line object going from point 1 to point 2.
	
	Args:
		p1 (numpy.ndarray): Coordinate of point 1.
		p2 (numpy.ndarray): Coordinate of point 2.
		
	Returns:
		vtk.vtkLine: VTK line object.
	
	"""
	
	line = vtk.vtkLineSource()
	line.SetPoint1(p1[0],p1[1],p1[2])
	line.SetPoint2(p2[0],p2[1],p2[2])
	
	return line

def drawVTKArc(pStart,pCenter,pEnd,color=[0,0,0],renderer=None,res=32):
	
	"""Draws VTK arc object defined through 3 points into renderer.
	
	If ``renderer=None``, will create actor but not add it to renderer.
	
	Args:
		pStart (numpy.ndarray): Coordinate of start point.
		pCenter (numpy.ndarray): Coordinate of center point.
		pEnd (numpy.ndarray): Coordinate of end point.
	
	Keyword Args:
		color (list): Color of sphere in normed RGB values.
		renderer (vtk.vtkRenderer): Renderer to draw in.
		res (int): Resolution of arc.
		
	Returns:
		vtk.vtkActor: VTK actor.
	
	"""
	
	arc=getVTKArc(pStart,pCenter,pEnd,res=res)
	
	actor=getVTKActor(color)
	actor.SetMapper(getVTKPolyDataMapper(getVTKOutput(arc)))
	
	if renderer!=None:
		renderer.AddActor(actor)
	
	return actor
	
def getVTKArc(pStart,pCenter,pEnd,res=32):
	
	"""Returns VTK arc object defined through 3 points.
	
	Args:
		pStart (numpy.ndarray): Coordinate of start point.
		pCenter (numpy.ndarray): Coordinate of center point.
		pEnd (numpy.ndarray): Coordinate of end point.
	
	Keyword Args:
		res (int): Resolution of arc.
		
	Returns:
		vtk.vtkActor: VTK actor.
	
	"""
	
	arc = vtk.vtkArcSource()
	arc.SetCenter( pCenter[0], pCenter[1], pCenter[2] )
	arc.SetPoint1( pStart[0], pStart[1], pStart[2] )
	arc.SetPoint2( pEnd[0], pEnd[1], pEnd[2] )
	arc.SetResolution( res )
	
	return arc
	
def getVTKActor(color):
	
	"""Returns VTK actor object and colors it.
	
	.. note:: Colors can also be given as matplotlib string colors.
	
	Args:
		color (list): Color of sphere in normed RGB values.
	
	Returns:
		vtk.vtkActor: VTK actor.
	
	"""
	
	color=np.asarray(matplotlib.colors.colorConverter.to_rgb(color))
	
	actor = vtk.vtkActor()
	actor.GetProperty().SetColor(color[0],color[1],color[2])
	
	return actor
	
def getVTKSphere(center,radius):
	
	"""Returns vtk source sphere object with given center and radius.
	
	Args:
		center (numpy.ndarray): Center of sphere.
		radius (float): Radius of sphere.
		
	Returns:
		vtk.vtkSphereSource: VTK sphere.
	
	"""
	
	source = vtk.vtkSphereSource()
	source.SetCenter(center[0],center[1],center[2])
	source.SetRadius(radius)
	
	return source

def drawVTKText(text,position,fontSize=18,color=[0,0,0],renderer=None):

	"""Draws text in renderer.
	
	Args:
		text (str): Text.
		position (numpy.ndarray): Position where to draw it.
	
	Keyword Args:
		fontSize (int): Font Size.
		color (list): Color of text in normed RGB values.
		renderer (vtk.vtkRenderer): Renderer to draw in.
	
	Returns:
		vtk.vtkTextActor: Text actor
	
	"""
	
	txt = vtk.vtkTextActor()
	txt.SetInput(text)
	txtprop=txt.GetTextProperty()
	txtprop.SetFontFamilyToArial()
	txtprop.SetFontSize(fontSize)
	txtprop.SetColor(color[0],color[1],color[2])
	txt.SetDisplayPosition(position[0],position[1])

	if renderer!=None:
		renderer.AddActor(txt)
	
	return txt
	
def getVTKOutput(obj):
	
	"""Returns the fitting vtk output.
	
	Fixes versioning problems between vtk versions 5 and older. 
	
	Args:
		obj (vtk.vtkObject): A VTK object.
		
	Returns:
		vtk.vtkPolyData: VTK poly data.
	
	"""
	
	if vtk.VTK_MAJOR_VERSION <= 5:
		return obj.GetOutput()
	else:
		return obj.GetOutputPort()

def getVTKPolyDataMapper(polyData):
	
	"""Returns a VTK poly data mapper.
	
	Fixes versioning problems between vtk versions 5 and older. 
	
	Args:
		obj (vtk.vtkPolyData): A VTK poly data object.
		
	Returns:
		vtk.vtkPolyDataMapper: VTK poly data mapper.
	
	"""
	
	mapper = vtk.vtkPolyDataMapper()
	if vtk.VTK_MAJOR_VERSION <= 5:
		mapper.SetInput(polyData)
	else:
		mapper.SetInputData(polyData)
		
	return mapper	