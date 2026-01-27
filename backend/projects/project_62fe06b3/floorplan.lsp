(defun c:GENPLAN ( / )
  ;; Project ID: Unknown
  ;; Building Type: residential
  ;; Last Modified: Unknown
  ;; Version: 1
  
  ;; Create layers
  (command "._LAYER" "N" "WALLS" "C" "7" "WALLS" "")
  (command "._LAYER" "N" "DOORS" "C" "3" "DOORS" "")
  (command "._LAYER" "N" "WINDOWS" "C" "5" "WINDOWS" "")
  (command "._LAYER" "N" "TEXT" "C" "2" "TEXT" "")
  
  ;; Set WALLS layer current
  (command "._LAYER" "S" "WALLS" "")
  
  ;; External boundary
  (command "._PLINE" "0,0" "4032,0" "4032,12398" "0,12398" "C")
  
  ;; Internal walls
  (command "._LINE" "0,0" "4032,0" "")
  (command "._LINE" "4032,0" "4032,4032" "")
  (command "._LINE" "0,4032" "2891,4032" "")
  (command "._LINE" "2891,4032" "2891,6923" "")
  (command "._LINE" "0,6923" "3475,6923" "")
  (command "._LINE" "3475,6923" "3475,10398" "")
  (command "._LINE" "0,10398" "1669,10398" "")
  (command "._LINE" "1669,10398" "1669,12398" "")
  
  ;; Doors
  (command "._LAYER" "S" "DOORS" "")
  (command "._LINE" "1566,0" "2466,0" "")
  (command "._ARC" "C" "1566,0" "2466,0" "1566,900" "")
  (command "._LINE" "0,5027" "0,5927" "")
  (command "._ARC" "C" "0,5027" "0,5927" "900,5027" "")
  (command "._LINE" "0,8210" "0,9110" "")
  (command "._ARC" "C" "0,8210" "0,9110" "900,8210" "")
  (command "._LINE" "0,10948" "0,11848" "")
  (command "._ARC" "C" "0,10948" "0,11848" "900,10948" "")
  
  ;; Room labels
  (command "._LAYER" "S" "TEXT" "")
  (command "._TEXT" "J" "MC" "2016.0,2016.0" "300" "0" "Living Room")
  (command "._TEXT" "J" "MC" "2016.0,1516.0" "200" "0" "175 sq.ft")
  (command "._TEXT" "J" "MC" "1445.5,5477.5" "300" "0" "Kitchen")
  (command "._TEXT" "J" "MC" "1445.5,4977.5" "200" "0" "90 sq.ft")
  (command "._TEXT" "J" "MC" "1737.5,8660.5" "300" "0" "Bedroom 1")
  (command "._TEXT" "J" "MC" "1737.5,8160.5" "200" "0" "130 sq.ft")
  (command "._TEXT" "J" "MC" "834.5,11398.0" "300" "0" "Bathroom 2")
  (command "._TEXT" "J" "MC" "834.5,10898.0" "200" "0" "30 sq.ft")
  
  (command "._ZOOM" "E")
  (princ "\nFloor plan generated successfully!")
  (princ)
)

(princ "\nType GENPLAN to generate the floor plan.")
(princ)