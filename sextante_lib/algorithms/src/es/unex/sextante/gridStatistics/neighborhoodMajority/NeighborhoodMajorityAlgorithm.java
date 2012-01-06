package es.unex.sextante.gridStatistics.neighborhoodMajority;

import java.util.HashMap;
import java.util.Iterator;
import java.util.Set;

import es.unex.sextante.core.Sextante;
import es.unex.sextante.gridStatistics.base.NeighborhoodStatsBaseAlgorithm;

public class NeighborhoodMajorityAlgorithm
         extends
            NeighborhoodStatsBaseAlgorithm {

   @Override
   public void defineCharacteristics() {

      setName(Sextante.getText("Mayority__neighbourhood"));
      setGroup(Sextante.getText("Focal_statistics"));
      super.defineCharacteristics();

   }


   @Override
   protected double processValues() {

      int i;
      int iCount;
      int iMaxCount = -1;
      double dValue;
      double dReturn = NO_DATA;
      Integer count;
      Double value;
      final HashMap map = new HashMap();

      for (i = 0; i < m_dValues.length; i++) {
         dValue = m_dValues[i];
         if (dValue != NO_DATA) {
            value = new Double(dValue);
            count = (Integer) map.get(new Double(dValue));
            if (count != null) {
               count = new Integer(count.intValue() + 1);
            }
            else {
               count = new Integer(1);
            }
            map.put(new Double(dValue), count);
         }
      }

      final Set set = map.keySet();
      final Iterator iter = set.iterator();

      while (iter.hasNext()) {
         value = (Double) iter.next();
         dValue = value.doubleValue();
         count = (Integer) map.get(value);
         iCount = count.intValue();
         if (iCount > iMaxCount) {
            dReturn = dValue;
            iMaxCount = iCount;
         }
         else if (iCount == iMaxCount) {
            dReturn = NO_DATA;
         }
      }

      return dReturn;

   }

}
