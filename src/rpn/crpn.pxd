



cdef extern from "rmnlib.h":
    #associate file_name with the file number iun
    #I don't know what is x, but in the example it was 0
    # options = 'STD+RND' in the example
    int c_fnom(int* iun, char* file_name, char* options, int x );

    int c_fstouv(int iun,  char* options);


    #for finding 2d lat/lons
    int  c_ezgdef_fmem(int ni, int nj, char* grtyp, char* e_l_s,
                               int ig1, int ig2, int ig3, int ig4,
                                                              float* lons, float* lats);

    int c_gdll(int ezgdef, float* lat_2d, float* lon_2d);


    #/*****************************************************************************
    #*                        C _ F S T I N F                                    *
    #*                                                                           *
    #*Object                                                                     *
    #*   Locate the next record that matches the research keys.                  *
    #*                                                                           *
    #*Arguments                                                                  *
    #*                                                                           *
    #*  IN  iun     unit number associated to the file                           *
    #*  OUT ni      dimension 1 of the data field                                *
    #*  OUT nj      dimension 2 of the data field                                *
    #*  OUT nk      dimension 3 of the data field                                *
    #*  IN  datev   valid date                                                   *
    #*  IN  etiket  label                                                        *
    #*  IN  ip1     vertical level                                               *
    #*  IN  ip2     forecast hour                                                *
    #*  IN  ip3     user defined identifier                                      *
    #*  IN  typvar  type of field                                                *
    #*  IN  nomvar  variable name                                                *
    #*                                                                           *
    #*****************************************************************************/
    #
    int c_fstinf(int iun, int *ni, int *nj, int *nk, int datev, char *in_etiket,
                                                         int ip1, int ip2, int ip3, char *in_typvar, char *in_nomvar);


    void c_fstlir(float* buffer, int iun, int *ni, int *nj, int* nk,
                                 int datev,  char* etiket, int ip1, int ip2, int ip3,
                                                                                 char* typvar,  char* nomvar);

    #/*****************************************************************************
    #*                         C _ F S T F R M                                   *
    #*                                                                           *
    #*Object                                                                     *
    #*   Closes a RPN standard file.                                             *
    #*                                                                           *
    #*Arguments                                                                  *
    #*                                                                           *
    #*  IN  iun     unit number associated to the file                           *
    #*                                                                           *
    #*****************************************************************************/
    int c_fstfrm(int iun);
    int c_fclos(int iun);


    #/*****************************************************************************
    #*                         C _ F S T L U K                                   *
    #*                                                                           *
    #*Object                                                                     *
    #*   Read the record at position given by handle.                            *
    #*                                                                           *
    #*Arguments                                                                  *
    #*                                                                           *
    #*  OUT field   data field to be read                                        *
    #*  IN  handle  positioning information to the record                        *
    #*  OUT ni      dimension 1 of the data field                                *
    #*  OUT nj      dimension 2 of the data field                                *
    #*  OUT nk      dimension 3 of the data field                                *
    #*                                                                           *
    #*****************************************************************************/

    int c_fstluk(float *field, int handle, int *ni, int *nj, int *nk);



    #/*****************************************************************************
    #*                         C _ F S T S U I                                   *
    #*                                                                           *
    #*Object                                                                     *
    #*   Finds the next record that matches the last search criterias            *
    #*                                                                           *
    #*Arguments                                                                  *
    #*                                                                           *
    #*  IN  iun     unit number associated to the file                           *
    #*  OUT ni      dimension 1 of the data field                                *
    #*  OUT nj      dimension 2 of the data field                                *
    #*  OUT nk      dimension 3 of the data field                                *
    #*                                                                           *
    #*****************************************************************************/
    #
    int c_fstsui(int iun, int *ni, int *nj, int *nk);

    #newdate
    #        *
    #        *AUTHOR   - E. BEAUCHESNE  -  JUN 96
    #        *
    #        *REVISION 001   M. Lepine, B.dugas - automne 2009/janvier 2010 -
    #        *               Ajouter le support des dates etendues (annees 0
    #        *               a 10000) via les nouveaux modes +- 5, 6 et 7.
    #        *REVISION 002   B.dugas - novembre 2010 - Correction au mode -7.
    #        *
    #        *LANGUAGE - fortran
    #        *
    #        *OBJECT(NEWDATE)
    #        *         - CONVERTS A DATE BETWEEN TWO OF THE FOLLOWING FORMATS:
    #        *           PRINTABLE DATE, CMC DATE-TIME STAMP(OLD OR NEW), TRUE DATE
    #        *
    #        *USAGE    - CALL NEWDATE(DAT1,DAT2,DAT3,MODE)
    #        *
    #        *ARGUMENTS
    #        * MODE CAN TAKE THE FOLLOWING VALUES:-7,-6,-5,-4,-3,-2,-1,1,2,3,4,5,6,7
    #        * MODE=1 : STAMP TO (TRUE_DATE AND RUN_NUMBER)
    #        *     OUT - DAT1 - THE TRUEDATE CORRESPONDING TO DAT2
    #        *      IN - DAT2 - CMC DATE-TIME STAMP (OLD OR NEW STYLE)
    #        *     OUT - DAT3 - RUN NUMBER OF THE DATE-TIME STAMP
    #        *      IN - MODE - SET TO 1
    #        * MODE=-1 : (TRUE_DATE AND RUN_NUMBER) TO STAMP
    #        *      IN - DAT1 - TRUEDATE TO BE CONVERTED
    #        *     OUT - DAT2 - CMC DATE-TIME STAMP (OLD OR NEW STYLE)
    #        *      IN - DAT3 - RUN NUMBER OF THE DATE-TIME STAMP
    #        *      IN - MODE - SET TO -1
    #        * MODE=2 : PRINTABLE TO TRUE_DATE
    #        *     OUT - DAT1 - TRUE_DATE
    #        *      IN - DAT2 - DATE OF THE PRINTABLE DATE (YYYYMMDD)
    #        *      IN - DAT3 - TIME OF THE PRINTABLE DATE (HHMMSSHH)
    #        *      IN - MODE - SET TO 2
    #        * MODE=-2 : TRUE_DATE TO PRINTABLE
    #        *      IN - DAT1 - TRUE_DATE
    #        *     OUT - DAT2 - DATE OF THE PRINTABLE DATE (YYYYMMDD)
    #        *     OUT - DAT3 - TIME OF THE PRINTABLE DATE (HHMMSSHH)
    #        *      IN - MODE - SET TO -2
    #        * MODE=3 : PRINTABLE TO STAMP
    #        *     OUT - DAT1 - CMC DATE-TIME STAMP (OLD OR NEW STYLE)
    #        *      IN - DAT2 - DATE OF THE PRINTABLE DATE (YYYYMMDD)
    #        *      IN - DAT3 - TIME OF THE PRINTABLE DATE (HHMMSSHH)
    #        *      IN - MODE - SET TO 3
    #        * MODE=-3 : STAMP TO PRINTABLE
    #        *      IN - DAT1 - CMC DATE-TIME STAMP (OLD OR NEW STYLE)
    #        *     OUT - DAT2 - DATE OF THE PRINTABLE DATE (YYYYMMDD)
    #        *     OUT - DAT3 - TIME OF THE PRINTABLE DATE (HHMMSSHH)
    #        *      IN - MODE - SET TO -3
    #        * MODE=4 : 14 word old style DATE array TO STAMP and array(14)
    #        *     OUT - DAT1 - CMC DATE-TIME STAMP (OLD OR NEW STYLE)
    #        *      IN - DAT2 - 14 word old style DATE array
    #        *      IN - DAT3 - UNUSED
    #        *      IN - MODE - SET TO 4
    #        * MODE=-4 : STAMP TO 14 word old style DATE array
    #        *      IN - DAT1 - CMC DATE-TIME STAMP (OLD OR NEW STYLE)
    #        *     OUT - DAT2 - 14 word old style DATE array
    #        *      IN - DAT3 - UNUSED
    #        *      IN - MODE - SET TO -4
    #        * MODE=5    PRINTABLE TO EXTENDED STAMP (year 0 to 10,000)
    #        *     OUT - DAT1 - EXTENDED DATE-TIME STAMP (NEW STYLE only)
    #        *      IN - DAT2 - DATE OF THE PRINTABLE DATE (YYYYMMDD)
    #        *      IN - DAT3 - TIME OF THE PRINTABLE DATE (HHMMSSHH)
    #        *      IN - MODE - SET TO 5
    #        * MODE=-5   EXTENDED STAMP (year 0 to 10,000) TO PRINTABLE
    #        *      IN - DAT1 - EXTENDED DATE-TIME STAMP (NEW STYLE only)
    #        *     OUT - DAT2 - DATE OF THE PRINTABLE DATE (YYYYMMDD)
    #        *     OUT - DAT3 - TIME OF THE PRINTABLE DATE (HHMMSSHH)
    #        *      IN - MODE - SET TO -5
    #        * MODE=6 :  EXTENDED STAMP TO EXTENDED TRUE_DATE (in hours)
    #        *     OUT - DAT1 - THE TRUEDATE CORRESPONDING TO DAT2
    #        *      IN - DAT2 - CMC DATE-TIME STAMP (OLD OR NEW STYLE)
    #        *     OUT - DAT3 - RUN NUMBER, UNUSED (0)
    #        *      IN - MODE - SET TO 6
    #        * MODE=-6 : EXTENDED TRUE_DATE (in hours) TO EXTENDED STAMP
    #        *      IN - DAT1 - TRUEDATE TO BE CONVERTED
    #        *     OUT - DAT2 - CMC DATE-TIME STAMP (OLD OR NEW STYLE)
    #        *      IN - DAT3 - RUN NUMBER, UNUSED
    #        *      IN - MODE - SET TO -6
    #        * MODE=7  - PRINTABLE TO EXTENDED TRUE_DATE (in hours)
    #        *     OUT - DAT1 - EXTENDED TRUE_DATE
    #        *      IN - DAT2 - DATE OF THE PRINTABLE DATE (YYYYMMDD)
    #        *      IN - DAT3 - TIME OF THE PRINTABLE DATE (HHMMSSHH)
    #        *      IN - MODE - SET TO 7
    #        * MODE=-7 : EXTENDED TRUE_DATE (in hours) TO PRINTABLE
    #        *      IN - DAT1 - EXTENDED TRUE_DATE
    #        *     OUT - DAT2 - DATE OF THE PRINTABLE DATE (YYYYMMDD)
    #        *     OUT - DAT3 - TIME OF THE PRINTABLE DATE (HHMMSSHH)
    #        *      IN - MODE - SET TO -7
    #        *NOTES    - IT IS RECOMMENDED TO ALWAYS USE THIS FUNCTION TO
    #        *           MANIPULATE DATES
    #        *         - IF MODE ISN'T IN THESE VALUES(-7,..,-2,-1,1,2,...,7) OR IF
    #        *           ARGUMENTS AREN'T VALID, NEWDATE HAS A RETURN VALUE OF 1
    #        *         - A TRUE DATE IS AN INTEGER (POSSIBLY NEGATIVE) THAT
    #        *           CONTAINS THE NUMBER OF 5 SECONDS INTERVALS SINCE
    #        *           1980/01/01 00H00. NEGATIVE VALUES ARISE AS
    #        *           THIS CONCEPT APPLIES FROM 1900/01/01.
    #        *         - AN EXTENDED TRUE DATE IS AN INTEGER THAT CONTAINS
    #        *           THE NUMBER OF HOURS SINCE YEAR 00/01/01
    #        *         - SEE INCDATR FOR DETAIL ON CMC DATE-TIME STAMP
    #        *
    #        *         useful constants
    #        *         17280 = nb of 5 sec intervals in a day
    #        *         288   = nb of 5 min intervals in a day
    #        *         jd1900 = julian day for jan 1, 1900       (2415021)
    #        *         jd1980 = julian day for jan 1, 1980       (2444240)
    #        *         jd2236 = julian day for jan 1, 2236       (2537742)
    #        *         jd0    = julian day for jan 1, 0          (1721060)
    #        *         jd10k  = julian day for jan 1, 10,000     (5373485)
    #        *         td1900 = truedate  for  jan 1, 1900 , 00Z (-504904320)
    #        *         td2000 = truedate  for  jan 1, 2000 , 00Z (+126230400)
    #        *         tdstart = base for newdates ( jan 1, 1980, 00Z)
    #        *         max_offset = (((jd10k-jd0)*24)/8)*10      (109572750)
    #        *         exception = extended truedate for jan 1, 1901, 01Z
    #        *         troisg = 3 000 000 000
    #        *WARNING  - IF NEWDATE RETURNS 1, OUTPUTS CAN TAKE ANY VALUE
    #        *

    int newdate_(int* dat1, int* dat2, int* dat3, int* mode);