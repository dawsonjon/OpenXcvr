unsigned keyer_state = IDLE;
void keyer(){
   switch(keyer_state){
       case IDLE:
	   settings.keyed = 0;
           if(DIT){
               keyer_state = DIT_STATE;
	   } else if(DAH){
	       keyer_state = DAH_STATE;
	   }
	   return;
       case DIT:
	   settings.keyed = 1;
	   keyer_state = DIT_SPACE;
	   return;
       case DAH:
	   settings.keyed = 1;
	   keyer_state = DAH_1;
           return;
       case DAH_1:
	   settings.keyed = 1;
	   keyer_state = DAH_2;
	   return;
       case DAH_2:
	   settings.keyed = 1;
	   keyer_state = DAH_3;
	   return;
       case DIT_SPACE:
	   settings.keyed = 0;
	   if(DAH){
	       keyer_state = DAH_STATE;
	   else if(DIT){
               keyer_state = DIT_STATE;
	   } else {
	       keyer_state = IDLE;
	   }
	   return;
       case DIT_SPACE:
	   settings.keyed = 0;
           if(DIT){
               keyer_state = DIT_STATE;
	   } else if(DAH){
	       keyer_state = DAH_STATE;
	   } else {
	       keyer_state = IDLE;
	   }
	   return;
   }
}
