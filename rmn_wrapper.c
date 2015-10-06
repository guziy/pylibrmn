
/***License notice for rmnlib C/Fortran library
    
    rmnlib fortran/C library
    Copyright (C) 2013  mfvalin

    This library is free software; you can redistribute it and/or
    modify it under the terms of the GNU Lesser General Public
    License as published by the Free Software Foundation; either
    version 2.1 of the License, or (at your option) any later version.

    This library is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public
    License along with this library; if not, write to the Free Software
    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
*/


//#include <iostream>

#include "rpn_macros_arch.h"
#include <rmnlib.h>

#include <stdio.h>
//using namespace std;

 //associate file_name with the file number iun
 //I don't know what is x, but in the example it was 0
 // options = 'STD+RND' in the example
int c_fnom(int* iun, char* file_name, char* options, int x );

int c_fstouv(int iun,  char* options);


//for finding 2d lat/lons
int  c_ezgdef_fmem(int ni, int nj, char* grtyp, char* e_l_s,
                                int ig1, int ig2, int ig3, int ig4,
                                float* lons, float* lats);

int c_gdll(int ezgdef, float* lat_2d, float* lon_2d);


/*****************************************************************************
 *                        C _ F S T I N F                                    *
 *                                                                           *
 *Object                                                                     *
 *   Locate the next record that matches the research keys.                  *
 *                                                                           *
 *Arguments                                                                  *
 *                                                                           *
 *  IN  iun     unit number associated to the file                           *
 *  OUT ni      dimension 1 of the data field                                *
 *  OUT nj      dimension 2 of the data field                                *
 *  OUT nk      dimension 3 of the data field                                *
 *  IN  datev   valid date                                                   *
 *  IN  etiket  label                                                        *
 *  IN  ip1     vertical level                                               *
 *  IN  ip2     forecast hour                                                *
 *  IN  ip3     user defined identifier                                      *
 *  IN  typvar  type of field                                                *
 *  IN  nomvar  variable name                                                *
 *                                                                           *
 *****************************************************************************/

int c_fstinf(int iun, int *ni, int *nj, int *nk, int datev,char *in_etiket,
                 int ip1, int ip2, int ip3, char *in_typvar, char *in_nomvar);


void c_fstlir(float* buffer, int iun, int *ni, int *nj, int* nk,
                   int datev,  char* etiket, int ip1, int ip2, int ip3,
                    char* typvar,  char* nomvar);

/*****************************************************************************
 *                         C _ F S T F R M                                   *
 *                                                                           *
 *Object                                                                     *
 *   Closes a RPN standard file.                                             *
 *                                                                           *
 *Arguments                                                                  *
 *                                                                           *
 *  IN  iun     unit number associated to the file                           *
 *                                                                           *
 *****************************************************************************/
int c_fstfrm(int iun);
int c_fclos(int iun);


/*****************************************************************************
 *                         C _ F S T L U K                                   *
 *                                                                           *
 *Object                                                                     *
 *   Read the record at position given by handle.                            *
 *                                                                           *
 *Arguments                                                                  *
 *                                                                           *
 *  OUT field   data field to be read                                        *
 *  IN  handle  positioning information to the record                        *
 *  OUT ni      dimension 1 of the data field                                *
 *  OUT nj      dimension 2 of the data field                                *
 *  OUT nk      dimension 3 of the data field                                *
 *                                                                           *
 *****************************************************************************/

int c_fstluk(float *field, int handle, int *ni, int *nj, int *nk);



/*****************************************************************************
 *                         C _ F S T S U I                                   *
 *                                                                           *
 *Object                                                                     *
 *   Finds the next record that matches the last search criterias            *
 *                                                                           *
 *Arguments                                                                  *
 *                                                                           *
 *  IN  iun     unit number associated to the file                           *
 *  OUT ni      dimension 1 of the data field                                *
 *  OUT nj      dimension 2 of the data field                                *
 *  OUT nk      dimension 3 of the data field                                *
 *                                                                           *
 *****************************************************************************/

int c_fstsui(int iun, int *ni, int *nj, int *nk);

extern  int fstsui_wrapper(int iun, int *ni, int *nj, int *nk){
   return c_fstsui(iun, ni, nj, nk);
}




/*****************************************************************************
 *                       C _ F S T P R M                                     *
 *                                                                           *
 *Object                                                                     *
 *   Get all the description informations of the record.                     *
 *                                                                           *
 *Rev 001 - M. Lepine - Oct 2002, returns extra1 as the validity datestamp   *
 *                                                                           *
 *Arguments                                                                  *
 *                                                                           *
 *  IN  handle  positioning information to the record                        *
 *  OUT date    date time stamp                                              *
 *  OUT deet    length of a time step in seconds                             *
 *  OUT npas    time step number                                             *
 *  OUT ni      first dimension of the data field                            *
 *  OUT nj      second dimension of the data field                           *
 *  OUT nk      third dimension of the data field                            *
 *  OUT nbits   number of bits kept for the elements of the field            *
 *  OUT datyp   data type of the elements                                    *
 *  OUT ip1     vertical level                                               *
 *  OUT ip2     forecast hour                                                *
 *  OUT ip3     user defined identifier                                      *
 *  OUT typvar  type of field (forecast, analysis, climatology)              *
 *  OUT nomvar  variable name                                                *
 *  OUT etiket  label                                                        *
 *  OUT grtyp   type of geographical projection                              *
 *  OUT ig1     first grid descriptor                                        *
 *  OUT ig2     second grid descriptor                                       *
 *  OUT ig3     third grid descriptor                                        *
 *  OUT ig4     fourth grid descriptor                                       *
 *  OUT swa     starting word address                                        *
 *  OUT lng     record length                                                *
 *  OUT dltf    delete flag                                                  *
 *  OUT ubc     unused bit count                                             *
 *  OUT extra1  extra parameter                                              *
 *  OUT extra2  extra parameter                                              *
 *  OUT extra3  extra parameter                                              *
 *                                                                           *
 *****************************************************************************/

extern  int c_fstprm(int handle,
             int *dateo, int *deet, int *npas,
             int *ni, int *nj, int *nk,
             int *nbits, int *datyp, int *ip1,
             int *ip2, int *ip3, char *typvar,
             char *nomvar, char *etiket, char *grtyp,
             int *ig1, int *ig2, int *ig3,
             int *ig4, int *swa, int *lng,
             int *dltf, int *ubc, int *extra1,
             int *extra2, int *extra3);


/*****************************************************************************
 *                          C _ I P 1 _ A L L                                *
 *                                                                           *
 *Object                                                                     *
 *   Generates all possible coded ip1 values for a given level               *
 *                                                                           *
 *Arguments                                                                  *
 *                                                                           *
 *  IN  level          ip1 level (float value)                               *
 *  IN  kind           level kind as defined in convip                       *
 *                                                                           *
 *****************************************************************************/

extern  int c_ip1_all(float level, int kind);


////////////////////////////////////////////////////////////////////////////////
//wrapper functions
extern  int fnom_wrapper(int* iun, char *file_name, char *options, int x){
    return c_fnom(iun, file_name, options, x );
}

extern  int fstouv_wrapper(int iun,  char* options){
    return c_fstouv( iun, options);
}

//gets a key of the field to find it in a file
extern  int fstinf_wrapper(int iun, int *ni, int *nj, int *nk, int datev,char *in_etiket,
                 int ip1, int ip2, int ip3, char *in_typvar, char *in_nomvar){
    int key;
    key = c_fstinf(iun, ni, nj, nk, datev, in_etiket, ip1, ip2, ip3, in_typvar, in_nomvar);
    return key;
}




extern int fstluk_wrapper(float *field, int handle, int *ni, int *nj, int *nk){
//    printf("Hello from C \n");
//    printf("handle = %d \n", handle);
//    printf("ni = %d \n", *ni);
    return c_fstluk(field, handle, ni, nj, nk);
}

extern  int fstprm_wrapper(int handle,
             int *dateo, int *deet, int *npas,
             int *ni, int *nj, int *nk,
             int *nbits, int *datyp, int *ip1,
             int *ip2, int *ip3, char *typvar,
             char *nomvar, char *etiket, char *grtyp,
             int *ig1, int *ig2, int *ig3,
             int *ig4, int *swa, int *lng,
             int *dltf, int *ubc, int *extra1,
             int *extra2, int *extra3){
    return c_fstprm(handle, dateo, deet, npas,
             ni, nj, nk,
             nbits, datyp, ip1,
             ip2, ip3, typvar,
             nomvar, etiket, grtyp,
             ig1, ig2, ig3,
             ig4, swa, lng,
             dltf, ubc, extra1,
             extra2, extra3);
}


extern  void fstlir_wrapper(float* buffer, int iun, int *ni, int *nj, int* nk,
                   int datev,  char* etiket, int ip1, int ip2, int ip3,
                    char* typvar,  char* nomvar){
    c_fstlir(buffer, iun, ni, nj, nk,
                  datev, etiket, ip1, ip2, ip3,
                  typvar, nomvar);
}

/**
 *
 * @param level
 * @param kind
 * @return ip coded level
 *
 * Ouput:    IP  =   Valeur codee
*            P    =   Valeur reelle
*               KIND =0, p est en hauteur (m) par rapport au niveau de la mer (-20,000 -> 100,000)
*               KIND =1, p est en sigma                                       (0.0 -> 1.0)
*               KIND =2, p est en pression (mb)                               (0 -> 1100)
*               KIND =3, p est un code arbitraire                             (-4.8e8 -> 10e10)
*               KIND =4, p est en hauteur (M) par rapport au niveau du sol    (-20,000 -> 100,000)
*               KIND =5, p est en coordonnee hybride                          (0.0 -> 1.0)
*               KIND =6, p est en coordonnee theta                            (1 -> 200,000)
*               KIND =10, p represente le temps en heure                      (0.0 -> 200,000.0)
*               KIND =15, reserve (entiers)
*               KIND =17, p represente l'indice x de la matrice de conversion (1.0 -> 1.0e10)
*               KIND =21, p est en metres-pression  (partage avec kind=5 a cause du range exclusif)
*                                                                             (0 -> 1,000,000) fact=1e4
 */
extern  int ip1_all_wrapper(float level, int kind){
    return c_ip1_all(level, kind);
}


/**
 * gets code of the crs to find 2d lat/lon fields
 * @param ni
 * @param nj
 * @param grtyp
 * @param e_l_s
 * @param ig1
 * @param ig2
 * @param ig3
 * @param ig4
 * @param lons
 * @param lats
 * @return
 */
extern  int  ezgdef_fmem_wrapper(int ni, int nj, char* grtyp, char* e_l_s,
                                int ig1, int ig2, int ig3, int ig4,
                                float* lons, float* lats){
    return c_ezgdef_fmem(ni, nj, grtyp,e_l_s, ig1, ig2, ig3, ig4,
                         lons, lats);
}

/**
 *
 * @param ezgdef
 * @param lats_2d - output
 * @param lons_2d - output
 * @return error code, if >= 0, all is ok
 */
extern  int gdll_wrapper(int ezgdef, float* lats_2d, float* lons_2d){
    int ier = c_gdll(ezgdef, lats_2d, lons_2d);
    return ier;
}


/**
 * close rpn file
 * @param iun
 * @return
 */
extern  int fstfrm_wrapper(int iun){
    return c_fstfrm(iun);
}

/**
 * close rpn file
 * @param iun
 * @return
 */
extern  int fclos_wrapper(int iun){
    return c_fclos(iun);
}


extern  char* get_message(){
    return "hello world";
}

extern  int get_number(){
    return 5;
}


/*****************************************************************************
 *                          C _ I P 2 _ A L L                                *
 *                                                                           *
 *Object                                                                     *
 *   Generates all possible coded ip2 values for a given level               *
 *                                                                           *
 *Arguments                                                                  *
 *                                                                           *
 *  IN  level          ip2 level (float value)                               *
 *  IN  kind           level kind as defined in convip                       *
 *                                                                           *
 *****************************************************************************/

extern  int c_ip2_all(float level, int kind);


extern  int ip2_all_wrapper(float level, int kind){
    return c_ip2_all(level, kind);
}


/*****************************************************************************
 *                          C _ I P 3 _ A L L                                *
 *                                                                           *
 *Object                                                                     *
 *   Generates all possible coded ip3 values for a given ip3                 *
 *                                                                           *
 *Arguments                                                                  *
 *                                                                           *
 *  IN  level          ip3  (float value)                                    *
 *  IN  kind           level kind as defined in convip                       *
 *                                                                           *
 *****************************************************************************/

extern  int c_ip3_all(float level, int kind);

extern  int ip3_all_wrapper(float level, int kind){
    return c_ip3_all(level, kind);
}



/**********************************************************************
*     Codage/Decodage P de/a IP pour IP1, IP2, IP3
*     necessaire avant de lire/ecrire un enregistrement
*     sur un fichier standard.
*
*     Etendu des valeurs encodes: 10e-5 -> 10e10
*     1024x1024-1 = 1048575    1048001 -> 1048575 non utilise
*
*     Auteurs: N. Ek et B. Dugas - Mars 1996
*     Revision 001  M. Lepine - juin 1997 convpr devient convip
*     Revision 002  M. Valin  - mai  1998 fichiers std 98
*     Revision 003  B. Dugas  - juillet 2000 code arbitraire
*     Revision 004  M. Lepine - fevrier 2002 kind = 4, hauteur au sol +
*                               possibilite de forcer newstyle ou non avec mode=2 et mode=3
*     Revision 005  M. Lepine - avril 2002 kind = 5 (hybride), kind = 21 (GalChen)
*                               valeur min, max, zero et facteur multiplicatif
*     Revision 006  M. Lepine - Juin 2002 kind = 6 (Theta)
*     Revision 007  M. Lepine - Oct 2003 kind = 10 (temps en heure)
*     Revision 008  M. Lepine - Dec 2005 kind = 17 (indice de matrice de niveaux)
*     Revision 009  M. Valin  - Mars 2008 kind = 21 (metres pression remplacant GalChen)
*                               introduction de zero_val2 pour la conversion ip->p
*
*     Input:    MODE = -1, de IP -->  P
*               MODE =  0, forcer conversion pour ip a 31 bits
*                          (default = ip a 15 bits)
*                          (appel d'initialisation)
*               MODE = +1, de P  --> IP
*               MODE = +2, de P  --> IP en mode NEWSTYLE force a true
*               MODE = +3, de P  --> IP en mode NEWSTYLE force a false
*               FLAG = .true. , ecriture de P avec format dans string
*
*     Input/
*     Ouput:    IP  =   Valeur codee
*               P    =   Valeur reelle
*               KIND =0, p est en hauteur (m) par rapport au niveau de la mer (-20,000 -> 100,000)
*               KIND =1, p est en sigma                                       (0.0 -> 1.0)
*               KIND =2, p est en pression (mb)                               (0 -> 1100)
*               KIND =3, p est un code arbitraire                             (-4.8e8 -> 10e10)
*               KIND =4, p est en hauteur (M) par rapport au niveau du sol    (-20,000 -> 100,000)
*               KIND =5, p est en coordonnee hybride                          (0.0 -> 1.0)
*               KIND =6, p est en coordonnee theta                            (1 -> 200,000)
*               KIND =10, p represente le temps en heure                      (0.0 -> 200,000.0)
*               KIND =15, reserve (entiers)
*               KIND =17, p represente l'indice x de la matrice de conversion (1.0 -> 1.0e10)
*               KIND =21, p est en metres-pression  (partage avec kind=5 a cause du range exclusif)
*                                                                             (0 -> 1,000,000) fact=1e4
*               STRING = valeur de P formattee
**********************************************************************/

extern  void f77name(convip)( int *ip, float *p, int *kind, int *mode, char* string, int* flag );
//ATTENTION
extern  void convip_wrapper(int *ip, float *p, int *kind, int *mode, char* str, int* flag){
    f77name(convip)(ip, p, kind, mode, str, flag);
}


/*****************************************************************************
 *                          C _ F S T N B R                                  *
 *                                                                           *
 *Object                                                                     *
 *   Returns the number of records of the file associated with unit number.  *
 *                                                                           *
 *Arguments                                                                  *
 *                                                                           *
 *  IN  iun     unit number associated to the file                           *
 *                                                                           *
 *****************************************************************************/

extern  int c_fstnbr(int iun);

extern  int fstnbr_wrapper(int iun){
    return c_fstnbr(iun);
}


/*splitpoint c_fstecr */
/*****************************************************************************
 *                           C _ F S T E C R                                 *
 *                                                                           *
 *Object                                                                     *
 *   Writes record to file.                                                  *
 *                                                                           *
 *Arguments                                                                  *
 *                                                                           *
 *  IN  field   field to write to the file                                   *
 *  IN  work    work field (kept for backward compatibility)                 *
 *  IN  npak    number of bits kept for the elements of the field (-npak)    *
 *  IN  iun     unit number associated to the file                           *
 *  IN  date    date time stamp                                              *
 *  IN  deet    length of a time step in seconds                             *
 *  IN  npas    time step number                                             *
 *  IN  ni      first dimension of the data field                            *
 *  IN  nj      second dimension of the data field                           *
 *  IN  nk      third dimension of the data field                            *
 *  IN  ip1     vertical level                                               *
 *  IN  ip2     forecast hour                                                *
 *  IN  ip3     user defined identifier                                      *
 *  IN  typvar  type of field (forecast, analysis, climatology)              *
 *  IN  nomvar  variable name                                                *
 *  IN  etiket  label                                                        *
 *  IN  grtyp   type of geographical projection                              *
 *  IN  ig1     first grid descriptor                                        *
 *  IN  ig2     second grid descriptor                                       *
 *  IN  ig3     third grid descriptor                                        *
 *  IN  ig4     fourth grid descriptor                                       *
 *  IN  datyp   data type of the elements                                    *
 *          0: binary, transparent                                           *
 *          1: floating point                                                *
 *          2: unsigned integer                                              *
 *          3: character (R4A in an integer)                                 *
 *          4: signed integer                                                *
 *          5: IEEE floating point                                           *
 *          6: floating point (16 bit, made for compressor)                  *
 *          7: character string                                              *
 *          8: complex IEEE                                                  *
 *        130: compressed short integer                                      *
 *        133: compressed IEEE                                               *
 *        134: compressed floating point                                     *
 *  IN  rewrit  rewrite flag (true=rewrite existing record, false=append)    *
 *                                                                           *
 *****************************************************************************/
extern  int c_fstecr(float *field, void * work, int npak,
                        int iun, int date,
                        int deet, int npas,
                        int ni, int nj, int nk,
                        int ip1, int ip2, int ip3,
                        char *in_typvar, char *in_nomvar, char *in_etiket,
                        char *in_grtyp, int ig1, int ig2,
                        int ig3, int ig4,
                        int in_datyp, int rewrit);


/**
 *
 * @param field
 * @param bits_per_value
 * @param iun
 * @param date
 * @param deet
 * @param npas
 * @param ni
 * @param nj
 * @param nk
 * @param ip1
 * @param ip2
 * @param ip3
 * @param in_typvar
 * @param in_nomvar
 * @param in_etiket
 * @param in_grtyp
 * @param datyp
 * @param rewrite if equal 1 then rewrite existing record
 * @return
 */
extern  int fstecr_wrapper(float* field, int bits_per_value, int iun,
                              int date, int deet, int npas,
                              int ni, int nj, int nk,
                              int ip1, int ip2, int ip3,
                              char *in_typvar, char *in_nomvar,
                              char *in_etiket, char *in_grtyp,
                              int ig1, int ig2, int ig3, int ig4,
                              int datyp, int rewrite){

    return c_fstecr(field, field, bits_per_value, iun, date, deet, npas,
                    ni, nj, nk, ip1, ip2, ip3, in_typvar, in_nomvar, in_etiket,
                    in_grtyp, ig1, ig2, ig3, ig4, datyp, rewrite );

}



/*
***S/P CXGAIG - PASSE DES PARAMETRES (REELS) DESCRIPTEURS DE GRILLE
              AUX PARAMETRES ENTIERS.

      SUBROUTINE CXGAIG(CGTYP,IG1,IG2,IG3,IG4,XG1,XG2,XG3,XG4)
      CHARACTER * 1 CGTYP
 *
 * folder base_010
 */

extern  void f77name(cxgaig)(char* grtype, int* ig1, int* ig2, int* ig3, int* ig4,
                                  float* xg1, float* xg2, float* xg3, float* xg4);

extern  void cxg_to_ig_wrapper(char* grtype, int* ig1, int* ig2, int* ig3, int* ig4,
                                  float* xg1, float* xg2, float* xg3, float* xg4){

    f77name(cxgaig)(grtype, ig1, ig2, ig3, ig4, xg1, xg2, xg3, xg4);
}




/* * Copyright (C) 1975-2001  Division de Recherche en Prevision Numerique
* *                          Environnement Canada
* *
* * This library is free software; you can redistribute it and/or
* * modify it under the terms of the GNU Lesser General Public
* * License as published by the Free Software Foundation,
* * version 2.1 of the License.
* *
* * This library is distributed in the hope that it will be useful,
* * but WITHOUT ANY WARRANTY; without even the implied warranty of
* * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
* * Lesser General Public License for more details.
* *
* * You should have received a copy of the GNU Lesser General Public
* * License along with this library; if not, write to the
* * Free Software Foundation, Inc., 59 Temple Place - Suite 330,
* * Boston, MA 02111-1307, USA.
* *
***S/P CIGAXG - PASSE DES PARAMETRES (ENTIERS) DESCRIPTEURS DE GRILLE
*              AUX PARAMETRES REELS.


      SUBROUTINE CIGAXG(CGTYP,XG1,XG2,XG3,XG4,IG1,IG2,IG3,IG4)
      CHARACTER * 1 CGTYP
 * */

extern  void f77name(cigaxg)(char* grtype, int* xg1, int* xg2, int* xg3, int* xg4,
                                  float* ig1, float* ig2, float* ig3, float* ig4);

extern  void cig_to_xg_wrapper(char* grtype, int* xg1, int* xg2, int* xg3, int* xg4,
                                  float* ig1, float* ig2, float* ig3, float* ig4){

    f77name(cigaxg)(grtype, xg1, xg2, xg3, xg4, ig1, ig2, ig3, ig4);
}



extern int f77name(newdate)(int* dat1, int* dat2, int* dat3, int* mode);

extern int newdate_wrapper(int* dat1, int* dat2, int* dat3, int* mode){
    return f77name(newdate)(dat1, dat2, dat3, mode);
}






/*****************************************************************************
 *                          C _ F S T O P C                                  *
 *                                                                           *
 *Object                                                                     *
 *   Print out or set a fstd or xdf global variable option.                  *
 *                                                                           *
 *Arguments                                                                  *
 *                                                                           *
 *   IN     option   option name to be set/printed                           *
 *   IN     value    option value                                            *
 *   IN     getmode  logical (1: get option, 0: set option)                  *
 *                                                                           *
 *****************************************************************************/
extern int c_fstopc(char *option, char *value, int getmode);

extern int fstopc_wrapper(char *option, char *value, int getmode){
    return c_fstopc(option, value, getmode);
}



/*****************************************************************************
 *                              F S T L N K                                  *
 *                                                                           *
 *Object                                                                     *
 *   Links a list of files together for search purpose.                      *
 *                                                                           *
 *Arguments                                                                  *
 *                                                                           *
 *  IN  liste   list of unit numbers associated to the files                 *
 *  IN  n       number of files to link                                      *
 *                                                                           *
 *****************************************************************************/

extern int c_xdflnk(word *liste, int *n);
extern int c_xdfunl(word *liste, int* n);

extern int fstlnk_wrapper(int *liste, int *n){
    return c_xdflnk(liste, n);
}

//unlink previously linked files
extern int fstunl_wrapper(int *liste, int *n){
    return c_xdfunl(liste, n);
}






