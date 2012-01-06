package es.unex.sextante.gui.batch.nonFileBased;

import java.util.ArrayList;

import javax.swing.table.AbstractTableModel;

import es.unex.sextante.additionalInfo.AdditionalInfoNumericalValue;
import es.unex.sextante.additionalInfo.AdditionalInfoSelection;
import es.unex.sextante.additionalInfo.AdditionalInfoString;
import es.unex.sextante.additionalInfo.AdditionalInfoVectorLayer;
import es.unex.sextante.core.OutputObjectsSet;
import es.unex.sextante.core.ParametersSet;
import es.unex.sextante.core.Sextante;
import es.unex.sextante.gui.core.SextanteGUI;
import es.unex.sextante.outputs.Output;
import es.unex.sextante.outputs.Output3DRasterLayer;
import es.unex.sextante.outputs.OutputRasterLayer;
import es.unex.sextante.outputs.OutputTable;
import es.unex.sextante.outputs.OutputVectorLayer;
import es.unex.sextante.parameters.Parameter;
import es.unex.sextante.parameters.Parameter3DRasterLayer;
import es.unex.sextante.parameters.ParameterBand;
import es.unex.sextante.parameters.ParameterBoolean;
import es.unex.sextante.parameters.ParameterDataObject;
import es.unex.sextante.parameters.ParameterNumericalValue;
import es.unex.sextante.parameters.ParameterRasterLayer;
import es.unex.sextante.parameters.ParameterSelection;
import es.unex.sextante.parameters.ParameterString;
import es.unex.sextante.parameters.ParameterVectorLayer;

/**
 * A Table model to be used for a batch process parameters panel
 * 
 * @author volaya
 * 
 */
public class ParametersTableModel
         extends
            AbstractTableModel {

   private final String[]      m_sColumnNames;
   private final ArrayList[]   m_Data;
   private final ParametersSet m_Parameters;

   public static final int     INIT_ROWS = 2;


   /**
    * Constructor
    * 
    * @param ps
    *                the set of input parameters to add to the table. A column will be added for each parameter
    * @param ooSet
    *                the set of outputs to add to the table. A column will be added for each output of type layer or table
    */
   public ParametersTableModel(final ParametersSet ps,
                               final OutputObjectsSet ooSet) {

      super();

      int i, j;

      m_Parameters = ps;

      m_sColumnNames = new String[ps.getNumberOfParameters() + ooSet.getOutputDataObjectsCount()];
      for (i = 0; i < ps.getNumberOfParameters(); i++) {
         m_sColumnNames[i] = ps.getParameter(i).getParameterDescription();
      }
      for (i = 0; i < ooSet.getOutputObjectsCount(); i++) {
         final Output out = ooSet.getOutput(i);
         if ((out instanceof OutputRasterLayer) || (out instanceof Output3DRasterLayer) || (out instanceof OutputVectorLayer)
             || (out instanceof OutputTable)) {
            m_sColumnNames[i + ps.getNumberOfParameters()] = out.getDescription();
         }
      }
      m_Data = new ArrayList[ps.getNumberOfParameters() + ooSet.getOutputDataObjectsCount()];

      for (i = 0; i < m_sColumnNames.length; i++) {
         m_Data[i] = new ArrayList();
         final Object def = getDefaultValue(i);
         for (j = 0; j < INIT_ROWS; j++) {
            m_Data[i].add(def);
         }
      }

   }


   /**
    * @return Number of columns(fields)
    */
   public int getColumnCount() {

      return m_sColumnNames.length;

   }


   /**
    * @return Number of rows
    */
   public int getRowCount() {

      return m_Data[0].size();

   }


   /**
    * @param iCol
    * @return Name of column iCol
    */
   @Override
   public String getColumnName(final int iCol) {

      return m_sColumnNames[iCol];

   }


   /**
    * 
    * @return An Array of strings with column names
    */
   public String[] getColumnNames() {

      return m_sColumnNames;

   }


   /**
    * @param iRow
    * @param iCol
    * @return Value at cell [iRow, iCol]
    */
   public Object getValueAt(final int iRow,
                            final int iCol) {

      return m_Data[iCol].get(iRow);

   }


   @Override
   public Class getColumnClass(final int c) {

      return getValueAt(0, c).getClass();

   }


   @Override
   public boolean isCellEditable(final int iRow,
                                 final int iCol) {

      return true;

   }


   @Override
   public void setValueAt(final Object value,
                          final int iRow,
                          final int iCol) {

      m_Data[iCol].set(iRow, value);
      fireTableCellUpdated(iRow, iCol);

   }


   /**
    * Adds a new row to the table (i.e. a new single algorithm execution)
    * 
    */
   public void addRow() {

      int i;

      for (i = 0; i < m_sColumnNames.length; i++) {
         final Object def = getDefaultValue(i);
         m_Data[i].add(def);
      }

      this.fireTableRowsInserted(m_Data[0].size(), m_Data[0].size());

   }


   /**
    * Removes a row
    * 
    * @param iRow
    *                the zero-based index of the row to remove
    */
   public void removeRow(final int iRow) {

      int i;
      for (i = 0; i < m_sColumnNames.length; i++) {
         m_Data[i].remove(iRow);
      }

      this.fireTableRowsDeleted(iRow, iRow);

   }


   private Object getDefaultValue(final int iIndex) {

      if (iIndex < m_Parameters.getNumberOfParameters()) {
         final Parameter parameter = m_Parameters.getParameter(iIndex);
         try {
            if (parameter instanceof ParameterDataObject) {
               Object objs[] = null;
               if (parameter instanceof ParameterRasterLayer) {
                  objs = SextanteGUI.getInputFactory().getRasterLayers();
               }
               else if (parameter instanceof Parameter3DRasterLayer) {
                  objs = SextanteGUI.getInputFactory().get3DRasterLayers();
               }
               else if (parameter instanceof ParameterVectorLayer) {
                  final AdditionalInfoVectorLayer ai = (AdditionalInfoVectorLayer) ((ParameterVectorLayer) parameter).getParameterAdditionalInfo();
                  objs = SextanteGUI.getInputFactory().getVectorLayers(ai.getShapeType());
               }
               else if (parameter instanceof ParameterRasterLayer) {
                  objs = SextanteGUI.getInputFactory().getTables();
               }
               if (objs != null) {
                  return objs[0];
               }
               else {
                  return "";
               }
            }
            else if (parameter instanceof ParameterBand) {
               return "1";
            }
            else if (parameter instanceof ParameterBoolean) {
               return "true";
            }
            else if (parameter instanceof ParameterSelection) {
               final AdditionalInfoSelection ai = (AdditionalInfoSelection) parameter.getParameterAdditionalInfo();
               return ai.getValues()[0];
            }
            else if (parameter instanceof ParameterString) {
               final AdditionalInfoString ai = (AdditionalInfoString) parameter.getParameterAdditionalInfo();
               return ai.getDefaultString();
            }
            else if (parameter instanceof ParameterNumericalValue) {
               final AdditionalInfoNumericalValue ai = (AdditionalInfoNumericalValue) parameter.getParameterAdditionalInfo();
               return Double.toString(ai.getDefaultValue());
            }
            else {
               return "";
            }
         }
         catch (final Exception e) {
            return "";
         }
      }
      else {
         return Sextante.getText("[Save_to_temporary_file]");
      }

   }


}
