#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GIMP Measure Annotate Plugin
Draws annotated measurement lines based on rectangular selection bounds.
Supports horizontal, vertical, and diagonal measurements.

GIMP 3.x only (GObject Introspection API)
"""

import gi
gi.require_version('Gimp', '3.0')
gi.require_version('GimpUi', '3.0')
gi.require_version('Gegl', '0.4')
from gi.repository import Gimp, GimpUi, Gegl, GObject, GLib
import math
import sys


def N_(message):
    """Mark string for translation without translating."""
    return message


def _(message):
    """Translate string."""
    return GLib.dgettext(None, message)


# -----------------------------------------------------------------------------
# Core Drawing Logic
# -----------------------------------------------------------------------------

def draw_measurement(image, x1, y1, x2, y2, label, orientation="diagonal"):
    """
    Draw a measurement line with text label on a new layer.
    
    Args:
        image: GimpImage to draw on
        x1, y1: Start point coordinates
        x2, y2: End point coordinates
        label: Text label to display (e.g., "150px")
        orientation: "horizontal", "vertical", or "diagonal"
    
    Returns:
        True on success, False on failure
    """
    # Start undo group
    image.undo_group_start()
    Gimp.context_push()
    
    try:
        # Create transparent annotation layer
        layer = Gimp.Layer.new(
            image,
            f"Measure: {label}",
            image.get_width(),
            image.get_height(),
            Gimp.ImageType.RGBA_IMAGE,
            100.0,  # opacity
            Gimp.LayerMode.NORMAL
        )
        layer.fill(Gimp.FillType.TRANSPARENT)
        
        # Insert layer at top
        image.insert_layer(layer, None, 0)
        
        # Set line color to red
        color = Gegl.Color.new("red")
        Gimp.context_set_foreground(color)
        
        # Set brush size for 2px line
        Gimp.context_set_brush_size(2.0)
        
        # Draw line using pencil
        # Coordinates as flat array: [x1, y1, x2, y2]
        coords = [float(x1), float(y1), float(x2), float(y2)]
        Gimp.pencil(layer, coords)
        
        # Calculate text position with proper offset based on orientation
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        
        # Create text layer first to get its dimensions
        text_layer = Gimp.TextLayer.new(
            image,
            label,
            Gimp.context_get_font(),
            14.0,  # font size
            Gimp.Unit.pixel()
        )
        image.insert_layer(text_layer, None, 0)
        
        # Get text dimensions
        text_width = text_layer.get_width()
        text_height = text_layer.get_height()
        
        # Calculate offset based on orientation
        if orientation == "horizontal":
            # Center horizontally, place above line
            text_x = mid_x - text_width / 2
            text_y = mid_y - text_height - 5
        elif orientation == "vertical":
            # Place to the left of line, center vertically
            text_x = mid_x - text_width - 8
            text_y = mid_y - text_height / 2
        else:  # diagonal
            # Calculate perpendicular offset based on line angle
            # Line goes from (x1,y1) to (x2,y2)
            dx = x2 - x1
            dy = y2 - y1
            line_length = math.sqrt(dx*dx + dy*dy)
            
            if line_length > 0:
                # Unit perpendicular vector (rotated 90° counterclockwise)
                # This puts text above/left of a line going down-right
                perp_x = -dy / line_length
                perp_y = dx / line_length
                
                # Offset distance from line
                offset_dist = text_height + 8
                
                # Position text centered on midpoint, offset perpendicular
                text_x = mid_x - text_width / 2 + perp_x * offset_dist
                text_y = mid_y - text_height / 2 + perp_y * offset_dist
            else:
                # Fallback for zero-length line
                text_x = mid_x - text_width / 2
                text_y = mid_y - text_height - 10
        
        text_layer.set_offsets(int(text_x), int(text_y))
        
        # Set text color to red
        text_layer.set_color(color)
        
        # Merge text layer into annotation layer
        merged = image.merge_down(text_layer, Gimp.MergeType.EXPAND_AS_NECESSARY)
        
        # Clear selection so marching ants don't obscure annotation
        Gimp.Selection.none(image)
        
        # Flush display
        Gimp.displays_flush()
        
        return True
        
    except Exception as e:
        Gimp.message(f"Error drawing measurement: {str(e)}")
        return False
        
    finally:
        Gimp.context_pop()
        image.undo_group_end()


def get_selection_bounds(image):
    """
    Get selection bounds from image.
    
    Returns:
        Tuple (success, x1, y1, x2, y2) or (False, 0, 0, 0, 0) if no selection
    """
    result = Gimp.Selection.bounds(image)
    # GIMP 3.x returns (success, non_empty, x1, y1, x2, y2)
    if len(result) == 6:
        success, non_empty, x1, y1, x2, y2 = result
        if not non_empty:
            Gimp.message("No selection found. Please make a rectangular selection first.")
            return False, 0, 0, 0, 0
        return True, x1, y1, x2, y2
    else:
        # Fallback for different API versions
        non_empty, x1, y1, x2, y2 = result
        if not non_empty:
            Gimp.message("No selection found. Please make a rectangular selection first.")
            return False, 0, 0, 0, 0
        return True, x1, y1, x2, y2


# -----------------------------------------------------------------------------
# Measurement Mode Functions
# -----------------------------------------------------------------------------

def measure_horizontal(image):
    """Draw horizontal measurement line across selection width."""
    success, x1, y1, x2, y2 = get_selection_bounds(image)
    if not success:
        return False
    
    # Horizontal line at vertical center
    center_y = (y1 + y2) / 2
    width = x2 - x1
    label = f"{width}px"
    
    return draw_measurement(image, x1, center_y, x2, center_y, label, "horizontal")


def measure_vertical(image):
    """Draw vertical measurement line across selection height."""
    success, x1, y1, x2, y2 = get_selection_bounds(image)
    if not success:
        return False
    
    # Vertical line at horizontal center
    center_x = (x1 + x2) / 2
    height = y2 - y1
    label = f"{height}px"
    
    return draw_measurement(image, center_x, y1, center_x, y2, label, "vertical")


def measure_diagonal(image):
    """Draw diagonal measurement line from top-left to bottom-right of selection."""
    success, x1, y1, x2, y2 = get_selection_bounds(image)
    if not success:
        return False
    
    # Diagonal line corner to corner
    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    label = f"{distance:.1f}px"
    
    return draw_measurement(image, x1, y1, x2, y2, label, "diagonal")


# -----------------------------------------------------------------------------
# Run Functions for Each Procedure
# -----------------------------------------------------------------------------

def run_measure_horizontal(procedure, run_mode, image, drawables, config, data):
    """Run function for horizontal measurement."""
    if run_mode == Gimp.RunMode.INTERACTIVE:
        GimpUi.init("python-fu-measure-horizontal")
    
    measure_horizontal(image)
    return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())


def run_measure_vertical(procedure, run_mode, image, drawables, config, data):
    """Run function for vertical measurement."""
    if run_mode == Gimp.RunMode.INTERACTIVE:
        GimpUi.init("python-fu-measure-vertical")
    
    measure_vertical(image)
    return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())


def run_measure_diagonal(procedure, run_mode, image, drawables, config, data):
    """Run function for diagonal measurement."""
    if run_mode == Gimp.RunMode.INTERACTIVE:
        GimpUi.init("python-fu-measure-diagonal")
    
    measure_diagonal(image)
    return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())


# -----------------------------------------------------------------------------
# Plugin Class
# -----------------------------------------------------------------------------

class MeasureAnnotate(Gimp.PlugIn):
    """GIMP 3.x Measure Annotate Plugin"""
    
    ## GimpPlugIn virtual methods ##
    def do_set_i18n(self, procname):
        return True, 'gimp30-python', None
    
    def do_query_procedures(self):
        return [
            'python-fu-measure-horizontal',
            'python-fu-measure-vertical',
            'python-fu-measure-diagonal'
        ]
    
    def do_create_procedure(self, name):
        if name == 'python-fu-measure-horizontal':
            procedure = Gimp.ImageProcedure.new(
                self, name,
                Gimp.PDBProcType.PLUGIN,
                run_measure_horizontal, None
            )
            procedure.set_menu_label(_("Measure _Horizontal"))
            procedure.set_documentation(
                _("Draw horizontal measurement line"),
                _("Draws a horizontal measurement line showing the width of the current selection"),
                name
            )
        
        elif name == 'python-fu-measure-vertical':
            procedure = Gimp.ImageProcedure.new(
                self, name,
                Gimp.PDBProcType.PLUGIN,
                run_measure_vertical, None
            )
            procedure.set_menu_label(_("Measure _Vertical"))
            procedure.set_documentation(
                _("Draw vertical measurement line"),
                _("Draws a vertical measurement line showing the height of the current selection"),
                name
            )
        
        elif name == 'python-fu-measure-diagonal':
            procedure = Gimp.ImageProcedure.new(
                self, name,
                Gimp.PDBProcType.PLUGIN,
                run_measure_diagonal, None
            )
            procedure.set_menu_label(_("Measure _Diagonal"))
            procedure.set_documentation(
                _("Draw diagonal measurement line"),
                _("Draws a diagonal measurement line showing the distance from top-left to bottom-right of the selection"),
                name
            )
        
        else:
            return None
        
        # Common settings for all procedures
        procedure.set_image_types("RGB*, GRAY*")
        procedure.set_sensitivity_mask(
            Gimp.ProcedureSensitivityMask.DRAWABLE
        )
        procedure.set_attribution(
            "Eric Hamilton",
            "Eric Hamilton",
            "2025"
        )
        procedure.add_menu_path("<Image>/Filters/Render/Measure")
        
        return procedure


Gimp.main(MeasureAnnotate.__gtype__, sys.argv)
