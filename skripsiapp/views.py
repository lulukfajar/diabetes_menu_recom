from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext
from .models import Makanan
from .models import JenisDiet
from .models import TingkatAktivitas
from .forms import FormMakanan
from scipy.optimize import linprog
import random
import pandas as pd
from django.template.loader import get_template
from xhtml2pdf import pisa

def landingpage(request):
  template = loader.get_template('landingpage.html')
  return HttpResponse(template.render())

def inputpage(request):
 data_makanan = Makanan.objects.all()
 tingkat_aktivitas = TingkatAktivitas.objects.all()
 return render(request, 'inputpage.html', {'data_makanan' : data_makanan, 'tingkat_aktivitas': tingkat_aktivitas})

def menupage(request):
  template = loader.get_template('inputpage2.html')
  return HttpResponse(template.render())

def adminindex(request):
  if request.user.is_authenticated:
    data = Makanan.objects.all()
    return render(request, 'adminindex.html', {'data' : data})
  else:
    return render(request, 'loginpage.html')

def createpage(request):
  if request.user.is_authenticated:
    return render(request, 'createpage.html')
  else:
    return render(request, 'loginpage.html')

def addmakanan(request):
  if request.method == 'POST':
    form = FormMakanan(request.POST)
    if form.is_valid():
      form.save()
      return redirect('adminindex')
  else:
    form = FormMakanan()
  return render(request, 'createpage.html', {'form': form})

def updatepage(request, id):
  if request.user.is_authenticated:
    data_makanan = get_object_or_404(Makanan, id=id)
    return render(request, 'updatepage.html', {'data_makanan': data_makanan})
  else:
    return render(request, 'loginpage.html')


def saveupdate(request, id):
  makanan = Makanan.objects.get(id=id)  
  form = FormMakanan(request.POST, instance = makanan)  
  if form.is_valid():  
    form.save()  
    return redirect("adminindex")  
  return render(request, 'updatepage.html', {'employee': makanan})

def delete(request, id):
  if request.user.is_authenticated:
    makanan = Makanan.objects.get(id=id)  
    makanan.delete()  
    return redirect("adminindex")
  else:
    return render(request, 'loginpage.html')

def loginpage(request):
  user = None
  if request.method == "GET":
    if request.user.is_authenticated:
      return redirect('adminindex')
    else:
      return render(request, 'loginpage.html')
  if request.method == "POST":
    username_login = request.POST['username']
    password_login = request.POST['password']
    user = authenticate(request, username=username_login, password=password_login)
    if user is not None:
      login(request, user)
      return redirect('adminindex')
    else:
      return redirect('loginpage')
  return render(request, 'loginpage.html')

@login_required
def user_logout(request):
  if request.method == "POST":
    if "logout" in request.POST:
      logout(request)
      return redirect('loginpage')	
  return render(request, 'loginpage.html')

def registrasipage(request):
  return render(request, 'registrasipage.html')

def export_pdf(request):
  if request.method == "POST":
    if "logout" in request.POST:
      logout(request)
      return redirect('loginpage')	
  return render(request, 'loginpage.html')


def prosesdata(request):
  data_personal       = {}
  jenis_kelamin_2     =''
  tingkat_aktivitas_2 =''
  penyakit_penyerta_2 =''
  data_gizi_harian    = {}

  data_makanan        = Makanan.objects.all()

  if request.method == 'POST':
    # try:
      nama          = request.POST.get('nama')
      jenis_kelamin = request.POST.get('jenis_kelamin')
      berat_badan   = request.POST.get('berat_badan')
      tinggi_badan  = request.POST.get('tinggi_badan')
      usia          = request.POST.get('usia')
      tingkat_aktivitas  = request.POST.getlist('tingkat_aktivitas')
      penyakit_penyerta  = request.POST.get('penyakit_penyerta')
      makanan_tidak_suka = request.POST.getlist('makanan_tidak_suka')
      alergi             = request.POST.getlist('alergi')
      kategori_harga     = request.POST.get('kategori_harga')
      tidak_ada          = "tidak_ada"
      
      if tidak_ada not in alergi:
        alergi_makanan_query = Makanan.objects.filter(id__in=alergi).values_list('nama', flat=True)
        if alergi_makanan_query:
            alergi_makanan = ', '.join(alergi_makanan_query)
        else:
            alergi_makanan = "-"
      else:
        alergi_makanan = "-"

      if jenis_kelamin == 'p':
        jenis_kelamin_2 = 'perempuan'
      else:
        jenis_kelamin_2 = 'laki-laki'

      if 'Berat' in tingkat_aktivitas :
        tingkat_aktivitas_2 = 'Berat'
        tingkat_aktivitas_p = 2
        tingkat_aktivitas_l = 2.1
      elif 'Sedang' in tingkat_aktivitas :
        tingkat_aktivitas_2 = 'Sedang'
        tingkat_aktivitas_p = 1.7
        tingkat_aktivitas_l = 1.76
      elif 'Ringan 1' in tingkat_aktivitas :
        tingkat_aktivitas_2 = 'Ringan'
        tingkat_aktivitas_p = 1.55
        tingkat_aktivitas_l = 1.65
      elif 'Sangat Ringan' in tingkat_aktivitas :
        tingkat_aktivitas_2 = 'Sangat Ringan'
        tingkat_aktivitas_p = 1.3
        tingkat_aktivitas_l = 1.3
      else:
        tingkat_aktivitas_2 = '-'
      
      if penyakit_penyerta == '1' :
        penyakit_penyerta_2 = 'dengan Kolesterol dalam darah yang tinggi'
        kode_penyakit = 'K02'
      elif penyakit_penyerta == '2':
        penyakit_penyerta_2 = 'dengan Komplikasi pembuluh darah'
        kode_penyakit = 'K03'
      elif penyakit_penyerta == '3':
        penyakit_penyerta_2 = 'yang telah menderita lebih dari 15 tahun'
        kode_penyakit = 'K04'
      elif penyakit_penyerta == '4':
        penyakit_penyerta_2 = 'dengan Stroke'
        kode_penyakit = 'K05'
      elif penyakit_penyerta == '5':
        penyakit_penyerta_2 = 'dengan Jantung Koroner'
        kode_penyakit = 'K05'
      elif penyakit_penyerta == '6':
        penyakit_penyerta_2 = 'dengan Infark Jantung'
        kode_penyakit = 'K05'
      elif penyakit_penyerta == '7':
        penyakit_penyerta_2 = 'dengan Penyakit pembuluh arteri perifer oklusif'
        kode_penyakit = 'K05'
      elif penyakit_penyerta == '8':
        penyakit_penyerta_2 = 'dengan Gangren'
        kode_penyakit = 'K06'
      else:
        penyakit_penyerta_2 = 'tanpa komplikasi'
        kode_penyakit = 'K01'

      data_personal = {
        'nama'          : nama,
        'jenis_kelamin' : jenis_kelamin_2,
        'berat_badan'   : berat_badan,
        'tinggi_badan'  : tinggi_badan,
        'usia'          : usia,
        'tingkat_aktivitas' : tingkat_aktivitas_2,
        'penyakit_penyerta' : penyakit_penyerta_2,
        'makanan_tidak_suka': makanan_tidak_suka,
        'alergi'            : alergi_makanan,
        'kategori_harga'    : kategori_harga,
      }

      bmi = float(berat_badan) /((float(tinggi_badan)*float(tinggi_badan))/10000)

      #Kategori BMI
      if bmi < 17:
        bmi_2 = 'Kekurangan berat badan tingkat berat'
        penambahan_kalori = 1.3 
        kode_imt = 'K07'
      elif 17 <= bmi < 18.5:
        bmi_2 = 'Kekurangan berat badan tingkat ringan'
        penambahan_kalori = 1.2
        kode_imt = 'K07'
      elif 18.5 <= bmi <= 25:
        bmi_2 = 'Normal'
        penambahan_kalori = 1
        kode_imt = 'K09'
      elif 25 < bmi <= 27:
        bmi_2 = 'Kelebihan berat badan tingkat ringan'
        penambahan_kalori = 0.8
        kode_imt = 'K08'
      elif bmi > 27:
        bmi_2 = 'Kelebihan berat badan tingkat berat'
        penambahan_kalori = 0.7
        kode_imt = 'K08'

      jenis_diet = JenisDiet.objects.get(kode_imt=kode_imt, kode_penyakit=kode_penyakit)
      
      kode_diet  = jenis_diet.kelompok_diet
      
      #Metode Harris Benedict
      if jenis_kelamin == 'p':
        amb = 655.096 + ( 9.563 * float(berat_badan)) + ( 1.850 * float(tinggi_badan) ) - (4.676 * float(usia))
        kalori_harian = amb * float(tingkat_aktivitas_p)
      else:
        amb = 66.473 + ( 13.752 * float(berat_badan)) + ( 5.003 * float(tinggi_badan)) - (6.755 * float(usia))
        kalori_harian = amb * float(tingkat_aktivitas_l)
    
      kalori_harian_final = round(kalori_harian * penambahan_kalori, 3)
      total_kalori  = kalori_harian_final + (kalori_harian_final * 0.1 )

      #pembagian protein, karbohidrat, dan lemak sesuai jenis penyakit
      if kode_diet == "G":
        total_karbo_actual   = round(kalori_harian_final * 0.6 / 4, 3)
        total_protein_actual = round(kalori_harian_final  * 0.2 / 4, 3)
        total_lemak_actual   = round(kalori_harian_final * 0.2 / 9, 3)
        total_karbo   = round((kalori_harian_final * 0.6 / 4)*1.1, 3)
        total_protein = round((kalori_harian_final * 0.2 / 4)*1.1, 3)
        total_lemak   = round((kalori_harian_final * 0.2 / 9)*1, 3)
      else:
        total_karbo_actual   = round(kalori_harian_final * 0.68 / 4, 3)
        total_protein_actual = round(kalori_harian_final * 0.12 / 4, 3)
        total_lemak_actual   = round(kalori_harian_final * 0.2 / 9, 3)
        total_karbo   = round((kalori_harian_final * 0.68 / 4)*1.2, 3)
        total_protein = round((kalori_harian_final * 0.12 / 4)*1.1, 3)
        total_lemak   = round((kalori_harian_final * 0.2 / 9)*1, 3)
      #Menghitung total zat gizi yang diperlukan 

      data_gizi_harian = {
        'bmi' : round(bmi, 3),
        'bmi_2' : bmi_2,
        'total_kalori'      : int(kalori_harian_final),
        'total_karbohidrat' : int(total_karbo_actual),
        'total_protein'     : int(total_protein_actual),
        'total_lemak'       : int(total_lemak_actual)
      }

      data_import = Makanan.objects.all()
      
      if tidak_ada not in alergi:
        data_import = data_import.exclude(id__in=alergi)

      if tidak_ada not in makanan_tidak_suka:
        data_import = data_import.exclude(id__in=makanan_tidak_suka)

      #mulai penerapan basis pengetahuan

      #pembagian gizi per waktu makan
      karbo_camilan   = total_karbo * 0.1
      lemak_camilan   = total_lemak * 0.1
      protein_camilan = total_protein * 0.1

      karbo_pagi      = total_karbo * 0.2
      protein_pagi    = total_protein * 0.2
      lemak_pagi      = total_lemak * 0.2

      karbo_siang     = total_karbo * 0.25
      protein_siang   = total_protein * 0.25
      lemak_siang     = total_lemak * 0.25

      #covert data to dataframe
      data_makanan = pd.DataFrame(list(data_import.values()))

      #memilih data dengan kolesterol rendah
      data_makanan     = data_makanan[data_makanan['kolesterol'] <= 100 ]

      if kode_diet == 'G' or kode_diet == 'KV':
        data_makanan     = data_makanan[data_makanan['dibatasi'] == 'Tidak' ]

      #data perkategori
      data_buah      = data_makanan[data_makanan['kategori'] == 'Buah']
      data_kacang    = data_makanan[data_makanan['kategori'] == 'kacang']
      data_skim_susu = data_makanan[data_makanan['kategori'] == 'Skim Susu']

      data_karbohidrat  = data_makanan[data_makanan['kategori'] == 'Karbohidrat']
      data_nasi         = data_karbohidrat[data_karbohidrat['nama'].str.contains('nasi', case=False)]
      data_lemak        = data_makanan[(data_makanan['kategori'] == 'Lemak') | (data_makanan['kategori'] == 'Lemak Hewani')]
      data_sayuran_a    = data_makanan[data_makanan['kategori'] == 'Sayuran A']
      data_sayuran_b    = data_makanan[data_makanan['kategori'] == 'Sayuran B']
      data_protein      = data_makanan[(data_makanan['kategori'] == 'Protein Nabati') | (data_makanan['kategori'] == 'Protein Hewani')]
      
      if kategori_harga != "":
        if kategori_harga == "1":
          data_protein_1 = data_protein[data_protein['harga'] < 3600]
          if len(data_protein_1) < 7:
            data_protein_1 = data_protein[data_protein['harga'] < 8000]
        elif kategori_harga == "2":
          data_protein_1 = data_protein[(data_protein['harga'] >= 3600) & (data_protein['harga'] <= 8000)]
          if len(data_protein_1) < 7:
            data_protein_1 = data_protein[data_protein['harga'] <= 8000]
        else:
          data_protein_1 = data_protein[data_protein['harga'] > 8000]
          if len(data_protein_1) < 7:
            data_protein_1 = data_protein[data_protein['harga'] > 3600]
            if len(data_protein_1) < 7:
              data_protein_1 = data_protein[data_protein['harga'] > 0]
        data_protein     = data_protein_1
        data_protein_1     = ""

      #Data protein untuk diet KV dan G
      if kode_diet == 'G' or kode_diet == 'KV':
        data_protein = data_protein[
            (data_protein['benam_bduabelas'] == 'Ada') &
            (data_protein['asam_folat'] == 'Ada') &
            (data_protein['asam_amino'] == 'Ada')
        ]
        
      protein_exclude   = []
      lemak_exclude     = []
      sayuran_a_exclude = []
      sayuran_b_exclude = []
      kacang_exclude    = []
      buah_exclude      = []

      menus             =[]

      for i in range(1, 6):
        total_kalori_i = 0
        while total_kalori_i < kalori_harian_final * 0.9:

          filtered_data_protein   = data_protein[~data_protein['id'].isin(protein_exclude)]
          filtered_data_sayuran_a = data_sayuran_a[~data_sayuran_a['id'].isin(sayuran_a_exclude)]
          filtered_data_sayuran_b = data_sayuran_b[~data_sayuran_b['id'].isin(sayuran_b_exclude)]
          filtered_data_buah      = data_buah[~data_buah['id'].isin(buah_exclude)]

          protein_i_exclude   = []
          sayuran_a_i_exclude = []
          sayuran_b_i_exclude = []
          buah_i_exclude      = []

          #Menu 1 Pagi
          karbohidrat_index    = random.randint(0, data_karbohidrat.shape[0] - 1)
          protein_index        = random.randint(0, filtered_data_protein.shape[0] - 1)
          lemak_index          = random.randint(0, data_lemak.shape[0] - 1)
          sayuran_a_index      = random.randint(0, filtered_data_sayuran_a.shape[0] - 1)
          sayuran_b_index      = random.randint(0, filtered_data_sayuran_b.shape[0] - 1)
          kacang_index         = random.randint(0, data_kacang.shape[0] - 1)
          buah_index           = random.randint(0, filtered_data_buah.shape[0] - 1)
          skim_susu_index      = random.randint(0, data_skim_susu.shape[0] - 1)

          # Ambil baris secara acak dari DataFrame
          karbohidrat_pagi_i  = data_karbohidrat.iloc[karbohidrat_index]
          protein_pagi_i      = filtered_data_protein.iloc[protein_index]
          lemak_pagi_i        = data_lemak.iloc[lemak_index]
          sayuran_a_pagi_i    = filtered_data_sayuran_a.iloc[sayuran_a_index]
          sayuran_b_pagi_i    = filtered_data_sayuran_b.iloc[sayuran_b_index]
          buah_pagi_i         = filtered_data_buah.iloc[buah_index]
          kacang_pagi_i       = data_kacang.iloc[kacang_index]
          skim_susu_pagi_i         = data_skim_susu.iloc[skim_susu_index]

          #Menu 1 Camilan Pagi
          A = [[kacang_pagi_i['karbohidrat']/100, buah_pagi_i['karbohidrat']/100, skim_susu_pagi_i['karbohidrat']/100],
              [kacang_pagi_i['protein']/100, buah_pagi_i['protein']/100, skim_susu_pagi_i['protein']/100],
              [kacang_pagi_i['lemak']/100, buah_pagi_i['lemak']/100, skim_susu_pagi_i['lemak']/100]]
          b = [karbo_camilan, protein_camilan, lemak_camilan]
          c = [-1, -1, -1]

          # Menentukan batasan-batasan variabel
          x2_bounds = (1, None)
          y2_bounds = (1, 125)
          z2_bounds = (0, 50)

          # Menyelesaikan permasalahan dengan metode simplex
          result = linprog(c, A_ub=A, b_ub=b, bounds=[x2_bounds, y2_bounds, z2_bounds])
          berat_kacang_pagi_i    = int(result.x[0])
          berat_buah_pagi_i      = int(result.x[1])
          berat_skim_susu_pagi_i = int(result.x[2])

          #Menu 1 Sarapan 
          A = [[karbohidrat_pagi_i['karbohidrat']/100, protein_pagi_i['karbohidrat']/100, lemak_pagi_i['karbohidrat']/100],
              [karbohidrat_pagi_i['protein']/100, protein_pagi_i['protein']/100, lemak_pagi_i['protein']/100],
              [karbohidrat_pagi_i['lemak']/100, protein_pagi_i['lemak']/100, lemak_pagi_i['lemak']/100]]
          b1 = [karbo_pagi - sayuran_a_pagi_i['karbohidrat'] - sayuran_b_pagi_i['karbohidrat']/4, protein_pagi - sayuran_a_pagi_i['protein'] - sayuran_b_pagi_i['protein']/4, lemak_pagi - sayuran_a_pagi_i['lemak'] - sayuran_b_pagi_i['lemak']/4]
          c = [-1, -1, -1]
          # Menentukan batasan-batasan variabel
          if kode_diet == "G":
            if kalori_harian_final <= 1500:
              x3_bounds = (1, 125)
              y3_bounds = (15, None)
            elif 1500 < kalori_harian_final < 2300:
              x3_bounds = (1, 150)
              y3_bounds = (20, None)
            elif 2300 <= kalori_harian_final < 2700:
              x3_bounds = (1, 200)
              y3_bounds = (20, None)
            else:
              x3_bounds = (1, 250)
              y3_bounds = (20, None)
          else:
            if kalori_harian_final <= 1500:
              x3_bounds = (1, 135)
              y3_bounds = (15, None)
            elif 1500 < kalori_harian_final < 2300:
              x3_bounds = (1, 150)
              y3_bounds = (20, None)
            elif 2300 <= kalori_harian_final < 2700:
              x3_bounds = (1, 200)
              y3_bounds = (20, None)
            elif 2700 <= kalori_harian_final <= 2900:
              x3_bounds = (1, 250)
              y3_bounds = (20, None)
            else:
              x3_bounds = (1, 300)
              y3_bounds = (20, None)
          z3_bounds = (0, None)
          # Menyelesaikan permasalahan dengan metode simplex
          
          max_iterasi = 100 
          for _ in range(max_iterasi):
              result = linprog(c, A_ub=A, b_ub=b1, bounds=[x3_bounds, y3_bounds, z3_bounds])
              if result is not None:
                  break

          berat_karbo_pagi_i   = int(result.x[0])
          berat_protein_pagi_i = int(result.x[1])
          berat_lemak_pagi_i   = int(result.x[2])

          protein_i_exclude.append(protein_pagi_i['id'])
          sayuran_a_i_exclude.append(sayuran_a_pagi_i['id'])
          sayuran_b_i_exclude.append(sayuran_b_pagi_i['id'])
          buah_i_exclude.append(buah_pagi_i['id'])

          filtered_data_protein   = data_protein[~data_protein['id'].isin(protein_i_exclude)]
          filtered_data_sayuran_a = data_sayuran_a[~data_sayuran_a['id'].isin(sayuran_a_i_exclude)]
          filtered_data_sayuran_b = data_sayuran_b[~data_sayuran_b['id'].isin(sayuran_b_i_exclude)]
          filtered_data_buah      = data_buah[~data_buah['id'].isin(buah_i_exclude)]
          
          #Menu 1 makan siang
          karbohidrat_index    = random.randint(0, data_nasi.shape[0] - 1)
          protein_index        = random.randint(0, filtered_data_protein.shape[0] - 1)
          lemak_index          = random.randint(0, data_lemak.shape[0] - 1)
          sayuran_a_index      = random.randint(0, filtered_data_sayuran_a.shape[0] - 1)
          sayuran_b_index      = random.randint(0, filtered_data_sayuran_b.shape[0] - 1)
          kacang_index         = random.randint(0, data_kacang.shape[0] - 1)
          buah_index           = random.randint(0, filtered_data_buah.shape[0] - 1)
          skim_susu_index      = random.randint(0, data_skim_susu.shape[0] - 1)

          # Ambil baris secara acak dari DataFrame
          karbohidrat_siang_i = data_nasi.iloc[karbohidrat_index]
          protein_siang_i     = filtered_data_protein.iloc[protein_index]
          lemak_siang_i       = data_lemak.iloc[lemak_index]
          sayuran_a_siang_i    = filtered_data_sayuran_a.iloc[sayuran_a_index]
          sayuran_b_siang_i    = data_sayuran_b.iloc[sayuran_b_index]
          buah_siang_i         = filtered_data_buah.iloc[buah_index]
          kacang_siang_i       = data_kacang.iloc[kacang_index]
          skim_susu_siang_i         = data_skim_susu.iloc[skim_susu_index]

          #Menu 1 Camilan siang
          A = [[kacang_siang_i['karbohidrat']/100, buah_siang_i['karbohidrat']/100, skim_susu_siang_i['karbohidrat']/100],
              [kacang_siang_i['protein']/100, buah_siang_i['protein']/100, skim_susu_siang_i['protein']/100],
              [kacang_siang_i['lemak']/100, buah_siang_i['lemak']/100, skim_susu_siang_i['lemak']/100]]
          b = [karbo_camilan, protein_camilan, lemak_camilan]

          # Menyelesaikan permasalahan dengan metode simplex
          result = linprog(c, A_ub=A, b_ub=b, bounds=[x2_bounds, y2_bounds, z2_bounds])
          berat_kacang_siang_i    = int(result.x[0])
          berat_buah_siang_i      = int(result.x[1])
          berat_skim_susu_siang_i = int(result.x[2])


          #Menu 1 berat makan siang
          A = [[karbohidrat_siang_i['karbohidrat']/100, protein_siang_i['karbohidrat']/100, lemak_siang_i['karbohidrat']/100],
              [karbohidrat_siang_i['protein']/100, protein_siang_i['protein']/100, lemak_siang_i['protein']/100],
              [karbohidrat_siang_i['lemak']/100, protein_siang_i['lemak']/100, lemak_siang_i['lemak']/100]]
          b1 = [karbo_siang - sayuran_a_siang_i['karbohidrat'] - sayuran_b_siang_i['karbohidrat']/2, protein_siang - sayuran_a_siang_i['protein'] - sayuran_b_siang_i['protein']/2, lemak_siang - sayuran_a_siang_i['lemak'] - sayuran_b_siang_i['lemak']/2]
          c = [-1, -1, -1]
          
          result2 = linprog(c, A_ub=A, b_ub=b1, bounds=[x3_bounds, y3_bounds, z3_bounds])
          berat_karbo_siang_i   = int(result2.x[0])
          berat_protein_siang_i = int(result2.x[1])
          berat_lemak_siang_i   = int(result2.x[2])

          protein_i_exclude.append(protein_siang_i['id'])
          sayuran_a_i_exclude.append(sayuran_a_siang_i['id'])
          sayuran_b_i_exclude.append(sayuran_b_siang_i['id'])
          buah_i_exclude.append(buah_siang_i['id'])

          filtered_data_protein   = data_protein[~data_protein['id'].isin(protein_i_exclude)]
          filtered_data_sayuran_a = data_sayuran_a[~data_sayuran_a['id'].isin(sayuran_a_i_exclude)]
          filtered_data_sayuran_b = data_sayuran_b[~data_sayuran_b['id'].isin(sayuran_b_i_exclude)]
          filtered_data_buah      = data_buah[~data_buah['id'].isin(buah_i_exclude)]

          #Menu 1 makan malam
          karbohidrat_index    = random.randint(0, data_nasi.shape[0] - 1)
          protein_index        = random.randint(0, filtered_data_protein.shape[0] - 1)
          lemak_index          = random.randint(0, data_lemak.shape[0] - 1)
          sayuran_a_index      = random.randint(0, filtered_data_sayuran_a.shape[0] - 1)
          sayuran_b_index      = random.randint(0, filtered_data_sayuran_b.shape[0] - 1)
          kacang_index         = random.randint(0, data_kacang.shape[0] - 1)
          buah_index           = random.randint(0, filtered_data_buah.shape[0] - 1)
          skim_susu_index      = random.randint(0, data_skim_susu.shape[0] - 1)

          # Ambil baris secara acak dari DataFrame
          karbohidrat_malam_i = data_nasi.iloc[karbohidrat_index]
          protein_malam_i     = filtered_data_protein.iloc[protein_index]
          lemak_malam_i       = data_lemak.iloc[lemak_index]
          sayuran_a_malam_i    = filtered_data_sayuran_a.iloc[sayuran_a_index]
          sayuran_b_malam_i    = data_sayuran_b.iloc[sayuran_b_index]
          buah_malam_i         = filtered_data_buah.iloc[buah_index]
          kacang_malam_i       = data_kacang.iloc[kacang_index]
          skim_susu_malam_i    = data_skim_susu.iloc[skim_susu_index]

          #Menu 1 Camilan malam
          A = [[kacang_malam_i['karbohidrat']/100, buah_malam_i['karbohidrat']/100, skim_susu_malam_i['karbohidrat']/100],
              [kacang_malam_i['protein']/100, buah_malam_i['protein']/100, skim_susu_malam_i['protein']/100],
              [kacang_malam_i['lemak']/100, buah_malam_i['lemak']/100, skim_susu_malam_i['lemak']/100]]
          b = [karbo_camilan, protein_camilan, lemak_camilan]

          # Menyelesaikan permasalahan dengan metode simplex
          result = linprog(c, A_ub=A, b_ub=b, bounds=[x2_bounds, y2_bounds, z2_bounds])
          berat_kacang_malam_i    = int(result.x[0])
          berat_buah_malam_i      = int(result.x[1])
          berat_skim_susu_malam_i = int(result.x[2])

          #Menu 1 berat makan malam
          A = [[karbohidrat_malam_i['karbohidrat']/100, protein_malam_i['karbohidrat']/100, lemak_malam_i['karbohidrat']/100],
              [karbohidrat_malam_i['protein']/100, protein_malam_i['protein']/100, lemak_malam_i['protein']/100],
              [karbohidrat_malam_i['lemak']/100, protein_malam_i['lemak']/100, lemak_malam_i['lemak']/100]]
          b1 = [karbo_siang - sayuran_a_malam_i['karbohidrat'] - sayuran_b_malam_i['karbohidrat']/2, protein_siang - sayuran_a_malam_i['protein'] - sayuran_b_malam_i['protein']/2, lemak_siang - sayuran_a_malam_i['lemak'] - sayuran_b_malam_i['lemak']/2]
          c = [-1, -1, -1]
          
          result2 = linprog(c, A_ub=A, b_ub=b1, bounds=[x3_bounds, y3_bounds, z3_bounds])
          berat_karbo_malam_i   = int(result2.x[0])
          berat_protein_malam_i = int(result2.x[1])
          berat_lemak_malam_i   = int(result2.x[2])

          protein_i_exclude.append(protein_malam_i['id'])
          sayuran_a_i_exclude.append(sayuran_a_malam_i['id'])
          sayuran_b_i_exclude.append(sayuran_b_malam_i['id'])
          buah_i_exclude.append(buah_siang_i['id'])

          total_karbohidrat_pagi_i = round(((karbohidrat_pagi_i['karbohidrat'] / 100) * berat_karbo_pagi_i) + ((protein_pagi_i['karbohidrat'] / 100) * berat_protein_pagi_i) + ((lemak_pagi_i['karbohidrat'] / 100) *berat_lemak_pagi_i)
          + (sayuran_a_pagi_i['karbohidrat']) + (0.25 * sayuran_b_pagi_i['karbohidrat'])
          + ((buah_pagi_i['karbohidrat'] / 100) * berat_buah_pagi_i) + ((kacang_pagi_i['karbohidrat'] / 100) * berat_kacang_pagi_i) + ((skim_susu_pagi_i['karbohidrat'] / 100) * berat_skim_susu_pagi_i), 3)

          total_karbohidrat_siang_i = round(((karbohidrat_siang_i['karbohidrat'] / 100) * berat_karbo_siang_i) + ((protein_siang_i['karbohidrat'] / 100) * berat_protein_siang_i) + ((lemak_siang_i['karbohidrat'] / 100) *berat_lemak_siang_i)
          + (sayuran_a_siang_i['karbohidrat']) + (0.5 * sayuran_b_siang_i['karbohidrat'])
          + ((buah_siang_i['karbohidrat'] / 100) * berat_buah_siang_i) + ((kacang_siang_i['karbohidrat'] / 100) * berat_kacang_siang_i) + ((skim_susu_siang_i['karbohidrat'] / 100) * berat_skim_susu_siang_i), 3)

          total_karbohidrat_malam_i = round(((karbohidrat_malam_i['karbohidrat'] / 100) * berat_karbo_malam_i) + ((protein_malam_i['karbohidrat'] / 100) * berat_protein_malam_i) + ((lemak_malam_i['karbohidrat'] / 100) *berat_lemak_malam_i)
          + (sayuran_a_malam_i['karbohidrat']) + (0.5 * sayuran_b_malam_i['karbohidrat'])
          + ((buah_malam_i['karbohidrat'] / 100) * berat_buah_malam_i) + ((kacang_malam_i['karbohidrat'] / 100) * berat_kacang_malam_i) + ((skim_susu_malam_i['karbohidrat'] / 100) * berat_skim_susu_malam_i), 3)

          total_protein_pagi_i = round(((karbohidrat_pagi_i['protein'] / 100) * berat_karbo_pagi_i) + ((protein_pagi_i['protein'] / 100) * berat_protein_pagi_i) + ((lemak_pagi_i['protein'] / 100) *berat_lemak_pagi_i)
          + (sayuran_a_pagi_i['protein']) + (0.25 * sayuran_b_pagi_i['protein'])
          + ((buah_pagi_i['protein'] / 100) * berat_buah_pagi_i) + ((kacang_pagi_i['protein'] / 100) * berat_kacang_pagi_i) + ((skim_susu_pagi_i['protein'] / 100) * berat_skim_susu_pagi_i), 3)

          total_protein_siang_i = round(((karbohidrat_siang_i['protein'] / 100) * berat_karbo_siang_i) + ((protein_siang_i['protein'] / 100) * berat_protein_siang_i) + ((lemak_siang_i['protein'] / 100) *berat_lemak_siang_i)
          + (sayuran_a_siang_i['protein']) + (0.5 * sayuran_b_siang_i['protein'])
          + ((buah_siang_i['protein'] / 100) * berat_buah_siang_i) + ((kacang_siang_i['protein'] / 100) * berat_kacang_siang_i) + ((skim_susu_siang_i['protein'] / 100) * berat_skim_susu_siang_i), 3)

          total_protein_malam_i = round(((karbohidrat_malam_i['protein'] / 100) * berat_karbo_malam_i) + ((protein_malam_i['protein'] / 100) * berat_protein_malam_i) + ((lemak_malam_i['protein'] / 100) *berat_lemak_malam_i)
          + (sayuran_a_malam_i['protein']) + (0.5 * sayuran_b_malam_i['protein'])
          + ((buah_malam_i['protein'] / 100) * berat_buah_malam_i) + ((kacang_malam_i['protein'] / 100) * berat_kacang_malam_i) + ((skim_susu_malam_i['protein'] / 100) * berat_skim_susu_malam_i), 3)

          total_lemak_pagi_i = round(((karbohidrat_pagi_i['lemak'] / 100) * berat_karbo_pagi_i) + ((protein_pagi_i['lemak'] / 100) * berat_protein_pagi_i) + ((lemak_pagi_i['lemak'] / 100) *berat_lemak_pagi_i)
          + (sayuran_a_pagi_i['lemak']) + (0.25 * sayuran_b_pagi_i['lemak'])
          + ((buah_pagi_i['lemak'] / 100) * berat_buah_pagi_i) + ((kacang_pagi_i['lemak'] / 100) * berat_kacang_pagi_i) + ((skim_susu_pagi_i['lemak'] / 100) * berat_skim_susu_pagi_i), 3)

          total_lemak_siang_i = round(((karbohidrat_siang_i['lemak'] / 100) * berat_karbo_siang_i) + ((protein_siang_i['lemak'] / 100) * berat_protein_siang_i) + ((lemak_siang_i['lemak'] / 100) *berat_lemak_siang_i)
          + (sayuran_a_siang_i['lemak']) + (0.5 * sayuran_b_siang_i['lemak'])
          + ((buah_siang_i['lemak'] / 100) * berat_buah_siang_i) + ((kacang_siang_i['lemak'] / 100) * berat_kacang_siang_i) + ((skim_susu_siang_i['lemak'] / 100) * berat_skim_susu_siang_i), 3)

          total_lemak_malam_i = round(((karbohidrat_malam_i['lemak'] / 100) * berat_karbo_malam_i) + ((protein_malam_i['lemak'] / 100) * berat_protein_malam_i) + ((lemak_malam_i['lemak'] / 100) *berat_lemak_malam_i)
          + (sayuran_a_malam_i['lemak']) + (0.5 * sayuran_b_malam_i['lemak'])
          + ((buah_malam_i['lemak'] / 100) * berat_buah_malam_i) + ((kacang_malam_i['lemak'] / 100) * berat_kacang_malam_i) + ((skim_susu_malam_i['lemak'] / 100) * berat_skim_susu_malam_i), 3)
          
          total_karbohidrat_i = int(total_karbohidrat_pagi_i + total_karbohidrat_siang_i + total_karbohidrat_malam_i)
          total_protein_i     = int(total_protein_pagi_i + total_protein_siang_i + total_protein_malam_i)
          total_lemak_i       = int(total_lemak_pagi_i + total_lemak_siang_i + total_lemak_malam_i)
          total_kalori_i      = int(total_karbohidrat_i * 4 + total_protein_i * 4 + total_lemak_i * 9)

          semua_nilai_i = [total_karbohidrat_i/total_karbo_actual, total_protein_i/total_protein_actual, total_lemak_i/total_lemak_actual, total_kalori_i/kalori_harian_final]
          nilai_tertinggi_i = round(max(semua_nilai_i)*100,3)
          nilai_terendah_i = round(min(semua_nilai_i)*100,3)
        menu_i = {
          'berat_buah_pagi'       : berat_buah_pagi_i,
          'berat_kacang_pagi'     : berat_kacang_pagi_i,
          'berat_skim_susu_pagi'  : berat_skim_susu_pagi_i,
          'berat_karbo_pagi'    : berat_karbo_pagi_i,
          'berat_protein_pagi'  : berat_protein_pagi_i,
          'berat_lemak_pagi'    : berat_lemak_pagi_i,
          'kacang_pagi'    : kacang_pagi_i['nama'],
          'buah_pagi'      : buah_pagi_i['nama'],
          'skim_susu_pagi' : skim_susu_pagi_i['nama'],
          'sayuran_a_pagi' : sayuran_a_pagi_i['nama'],
          'sayuran_b_pagi' : sayuran_b_pagi_i['nama'],
          'karbohidrat_pagi': karbohidrat_pagi_i['nama'],
          'protein_pagi'   : protein_pagi_i['nama'],
          'lemak_pagi'     : lemak_pagi_i['nama'],
          'berat_buah_siang'       : berat_buah_siang_i,
          'berat_kacang_siang'     : berat_kacang_siang_i,
          'berat_skim_susu_siang'  : berat_skim_susu_siang_i,
          'berat_karbo_siang'    : berat_karbo_siang_i,
          'berat_protein_siang'  : berat_protein_siang_i,
          'berat_lemak_siang'    : berat_lemak_siang_i,
          'kacang_siang'    : kacang_siang_i['nama'],
          'buah_siang'      : buah_siang_i['nama'],
          'skim_susu_siang' : skim_susu_siang_i['nama'],
          'sayuran_a_siang' : sayuran_a_siang_i['nama'],
          'sayuran_b_siang' : sayuran_b_siang_i['nama'],
          'karbohidrat_siang': karbohidrat_siang_i['nama'],
          'protein_siang'   : protein_siang_i['nama'],
          'lemak_siang'     : lemak_siang_i['nama'],
          'berat_buah_malam'       : berat_buah_malam_i,
          'berat_kacang_malam'     : berat_kacang_malam_i,
          'berat_skim_susu_malam'  : berat_skim_susu_malam_i,
          'berat_karbo_malam'    : berat_karbo_malam_i,
          'berat_protein_malam'  : berat_protein_malam_i,
          'berat_lemak_malam'    : berat_lemak_malam_i,
          'kacang_malam'    : kacang_malam_i['nama'],
          'buah_malam'      : buah_malam_i['nama'],
          'skim_susu_malam' : skim_susu_malam_i['nama'],
          'sayuran_a_malam' : sayuran_a_malam_i['nama'],
          'sayuran_b_malam' : sayuran_b_malam_i['nama'],
          'karbohidrat_malam': karbohidrat_malam_i['nama'],
          'protein_malam'   : protein_malam_i['nama'],
          'lemak_malam'     : lemak_malam_i['nama'],
          'total_karbo'     : total_karbohidrat_i,
          'total_protein'   : total_protein_i,
          'total_lemak'     : total_lemak_i,
          'total_kalori'    : total_kalori_i,
          'nilai_max'       : nilai_tertinggi_i,
          'nilai_min'       : nilai_terendah_i,
        }

        menus.append(menu_i)
        
        if len(filtered_data_protein)-len(protein_i_exclude) > 15-3*i:
          protein_exclude.extend(protein_i_exclude)
        else:
          protein_exclude=[]
        if len(filtered_data_sayuran_a)-len(sayuran_a_i_exclude) > 15-3*i:
          sayuran_a_exclude.extend(sayuran_a_i_exclude)
        else:
          sayuran_a_exclude=[]
        if len(filtered_data_sayuran_b)-len(sayuran_b_i_exclude) > 15-3*i:
          sayuran_b_exclude.extend(sayuran_b_i_exclude)
        else:
          sayuran_b_exclude=[]
        if len(filtered_data_buah)-len(buah_exclude) > 15-3*i:
          buah_exclude.extend(buah_i_exclude)
        else:
          buah_exclude=[]
      array_range = [1,2,3,4,5]
      return render(request, 'menupage.html', {'data_personal': data_personal, 'data_gizi_harian' : data_gizi_harian, 'jenis_diet' : jenis_diet, 'menu' : menus, 'array_range' : array_range})
    
    # except Exception as e:
    #   return render(request, 'errorhandling.html')
  tingkat_aktivitas = TingkatAktivitas.objects.all()
  return render(request, 'inputpage.html', {'data_makanan' : data_makanan, 'tingkat_aktivitas' : tingkat_aktivitas})

def export_pdf(request):

  if request.method == "POST":
    nama          = request.POST.get('nama')
    jenis_kelamin = request.POST.get('jenis_kelamin')
    berat_badan   = request.POST.get('berat_badan')
    tinggi_badan  = request.POST.get('tinggi_badan')
    usia          = request.POST.get('usia')
    tingkat_aktivitas  = request.POST.get('tingkat_aktivitas')
    penyakit_penyerta  = request.POST.get('penyakit_penyerta')
    makanan_tidak_suka = request.POST.get('makanan_tidak_suka')
    alergi             = request.POST.get('alergi')
    kategori_harga     = request.POST.get('kategori_harga')

    bmi          = request.POST.get('bmi')
    bmi_2        = request.POST.get('bmi_2')
    total_kalori = request.POST.get('total_kalori')
    total_karbohidrat = request.POST.get('total_karbohidrat')
    total_protein     = request.POST.get('total_protein')
    total_lemak       = request.POST.get('total_lemak')

    berat_buah_pagi_1     = request.POST.get('berat_buah_pagi_1')
    berat_kacang_pagi_1   = request.POST.get('berat_kacang_pagi_1')
    berat_skim_susu_pagi_1= request.POST.get('berat_skim_susu_pagi_1')
    berat_karbo_pagi_1    = request.POST.get('berat_karbo_pagi_1')
    berat_protein_pagi_1  = request.POST.get('berat_protein_pagi_1')
    berat_lemak_pagi_1    = request.POST.get('berat_lemak_pagi_1')
    berat_buah_siang_1    = request.POST.get('berat_buah_siang_1')
    berat_kacang_siang_1   = request.POST.get('berat_kacang_siang_1')
    berat_skim_susu_siang_1= request.POST.get('berat_skim_susu_siang_1')
    berat_karbo_siang_1    = request.POST.get('berat_karbo_siang_1')
    berat_protein_siang_1  = request.POST.get('berat_protein_siang_1')
    berat_lemak_siang_1    = request.POST.get('berat_lemak_siang_1')
    berat_buah_malam_1     = request.POST.get('berat_buah_malam_1')
    berat_kacang_malam_1   = request.POST.get('berat_kacang_malam_1')
    berat_skim_susu_malam_1= request.POST.get('berat_skim_susu_malam_1')
    berat_karbo_malam_1    = request.POST.get('berat_karbo_malam_1')
    berat_protein_malam_1  = request.POST.get('berat_protein_malam_1')
    berat_lemak_malam_1    = request.POST.get('berat_lemak_malam_1')
    buah_pagi_1            = request.POST.get('buah_pagi_1')
    kacang_pagi_1          = request.POST.get('kacang_pagi_1')
    skim_susu_pagi_1       = request.POST.get('skim_susu_pagi_1')
    karbohidrat_pagi_1     = request.POST.get('karbohidrat_pagi_1')
    protein_pagi_1         = request.POST.get('protein_pagi_1')
    lemak_pagi_1           = request.POST.get('lemak_pagi_1')
    sayuran_a_pagi_1       = request.POST.get('sayuran_a_pagi_1')
    sayuran_b_pagi_1       = request.POST.get('sayuran_b_pagi_1')
    buah_siang_1           = request.POST.get('buah_siang_1')
    kacang_siang_1         = request.POST.get('kacang_siang_1')
    skim_susu_siang_1      = request.POST.get('skim_susu_siang_1')
    karbohidrat_siang_1    = request.POST.get('karbohidrat_siang_1')
    protein_siang_1        = request.POST.get('protein_siang_1')
    lemak_siang_1          = request.POST.get('lemak_siang_1')
    sayuran_a_siang_1      = request.POST.get('sayuran_a_siang_1')
    sayuran_b_siang_1      = request.POST.get('sayuran_b_siang_1')
    buah_malam_1           = request.POST.get('buah_malam_1')
    kacang_malam_1         = request.POST.get('kacang_malam_1')
    skim_susu_malam_1      = request.POST.get('skim_susu_malam_1')
    karbohidrat_malam_1    = request.POST.get('karbohidrat_malam_1')
    protein_malam_1        = request.POST.get('protein_malam_1')
    lemak_malam_1          = request.POST.get('lemak_malam_1')
    sayuran_a_malam_1      = request.POST.get('sayuran_a_malam_1')
    sayuran_b_malam_1      = request.POST.get('sayuran_b_malam_1')
    total_karbohidrat_1   = request.POST.get('total_karbohidrat_1')
    total_protein_1       = request.POST.get('total_protein_1')
    total_lemak_1         = request.POST.get('total_lemak_1')
    total_kalori_1        = request.POST.get('total_kalori_1')

    berat_buah_pagi_2     = request.POST.get('berat_buah_pagi_2')
    berat_kacang_pagi_2   = request.POST.get('berat_kacang_pagi_2')
    berat_skim_susu_pagi_2= request.POST.get('berat_skim_susu_pagi_2')
    berat_karbo_pagi_2    = request.POST.get('berat_karbo_pagi_2')
    berat_protein_pagi_2  = request.POST.get('berat_protein_pagi_2')
    berat_lemak_pagi_2    = request.POST.get('berat_lemak_pagi_2')
    berat_buah_siang_2    = request.POST.get('berat_buah_siang_2')
    berat_kacang_siang_2   = request.POST.get('berat_kacang_siang_2')
    berat_skim_susu_siang_2= request.POST.get('berat_skim_susu_siang_2')
    berat_karbo_siang_2    = request.POST.get('berat_karbo_siang_2')
    berat_protein_siang_2  = request.POST.get('berat_protein_siang_2')
    berat_lemak_siang_2    = request.POST.get('berat_lemak_siang_2')
    berat_buah_malam_2     = request.POST.get('berat_buah_malam_2')
    berat_kacang_malam_2   = request.POST.get('berat_kacang_malam_2')
    berat_skim_susu_malam_2= request.POST.get('berat_skim_susu_malam_2')
    berat_karbo_malam_2    = request.POST.get('berat_karbo_malam_2')
    berat_protein_malam_2  = request.POST.get('berat_protein_malam_2')
    berat_lemak_malam_2    = request.POST.get('berat_lemak_malam_2')
    buah_pagi_2            = request.POST.get('buah_pagi_2')
    kacang_pagi_2          = request.POST.get('kacang_pagi_2')
    skim_susu_pagi_2       = request.POST.get('skim_susu_pagi_2')
    karbohidrat_pagi_2     = request.POST.get('karbohidrat_pagi_2')
    protein_pagi_2         = request.POST.get('protein_pagi_2')
    lemak_pagi_2           = request.POST.get('lemak_pagi_2')
    sayuran_a_pagi_2       = request.POST.get('sayuran_a_pagi_2')
    sayuran_b_pagi_2       = request.POST.get('sayuran_b_pagi_2')
    buah_siang_2           = request.POST.get('buah_siang_2')
    kacang_siang_2         = request.POST.get('kacang_siang_2')
    skim_susu_siang_2      = request.POST.get('skim_susu_siang_2')
    karbohidrat_siang_2    = request.POST.get('karbohidrat_siang_2')
    protein_siang_2        = request.POST.get('protein_siang_2')
    lemak_siang_2          = request.POST.get('lemak_siang_2')
    sayuran_a_siang_2      = request.POST.get('sayuran_a_siang_2')
    sayuran_b_siang_2      = request.POST.get('sayuran_b_siang_2')
    buah_malam_2           = request.POST.get('buah_malam_2')
    kacang_malam_2         = request.POST.get('kacang_malam_2')
    skim_susu_malam_2      = request.POST.get('skim_susu_malam_2')
    karbohidrat_malam_2    = request.POST.get('karbohidrat_malam_2')
    protein_malam_2        = request.POST.get('protein_malam_2')
    lemak_malam_2          = request.POST.get('lemak_malam_2')
    sayuran_a_malam_2      = request.POST.get('sayuran_a_malam_2')
    sayuran_b_malam_2      = request.POST.get('sayuran_b_malam_2')
    total_karbohidrat_2   = request.POST.get('total_karbohidrat_2')
    total_protein_2       = request.POST.get('total_protein_2')
    total_lemak_2         = request.POST.get('total_lemak_2')
    total_kalori_2        = request.POST.get('total_kalori_2')

    berat_buah_pagi_3     = request.POST.get('berat_buah_pagi_3')
    berat_kacang_pagi_3   = request.POST.get('berat_kacang_pagi_3')
    berat_skim_susu_pagi_3= request.POST.get('berat_skim_susu_pagi_3')
    berat_karbo_pagi_3    = request.POST.get('berat_karbo_pagi_3')
    berat_protein_pagi_3  = request.POST.get('berat_protein_pagi_3')
    berat_lemak_pagi_3    = request.POST.get('berat_lemak_pagi_3')
    berat_buah_siang_3    = request.POST.get('berat_buah_siang_3')
    berat_kacang_siang_3   = request.POST.get('berat_kacang_siang_3')
    berat_skim_susu_siang_3= request.POST.get('berat_skim_susu_siang_3')
    berat_karbo_siang_3    = request.POST.get('berat_karbo_siang_3')
    berat_protein_siang_3  = request.POST.get('berat_protein_siang_3')
    berat_lemak_siang_3    = request.POST.get('berat_lemak_siang_3')
    berat_buah_malam_3     = request.POST.get('berat_buah_malam_3')
    berat_kacang_malam_3   = request.POST.get('berat_kacang_malam_3')
    berat_skim_susu_malam_3= request.POST.get('berat_skim_susu_malam_3')
    berat_karbo_malam_3    = request.POST.get('berat_karbo_malam_3')
    berat_protein_malam_3  = request.POST.get('berat_protein_malam_3')
    berat_lemak_malam_3    = request.POST.get('berat_lemak_malam_3')
    buah_pagi_3            = request.POST.get('buah_pagi_3')
    kacang_pagi_3          = request.POST.get('kacang_pagi_3')
    skim_susu_pagi_3       = request.POST.get('skim_susu_pagi_3')
    karbohidrat_pagi_3     = request.POST.get('karbohidrat_pagi_3')
    protein_pagi_3         = request.POST.get('protein_pagi_3')
    lemak_pagi_3           = request.POST.get('lemak_pagi_3')
    sayuran_a_pagi_3       = request.POST.get('sayuran_a_pagi_3')
    sayuran_b_pagi_3       = request.POST.get('sayuran_b_pagi_3')
    buah_siang_3           = request.POST.get('buah_siang_3')
    kacang_siang_3         = request.POST.get('kacang_siang_3')
    skim_susu_siang_3      = request.POST.get('skim_susu_siang_3')
    karbohidrat_siang_3    = request.POST.get('karbohidrat_siang_3')
    protein_siang_3        = request.POST.get('protein_siang_3')
    lemak_siang_3          = request.POST.get('lemak_siang_3')
    sayuran_a_siang_3      = request.POST.get('sayuran_a_siang_3')
    sayuran_b_siang_3      = request.POST.get('sayuran_b_siang_3')
    buah_malam_3           = request.POST.get('buah_malam_3')
    kacang_malam_3         = request.POST.get('kacang_malam_3')
    skim_susu_malam_3      = request.POST.get('skim_susu_malam_3')
    karbohidrat_malam_3    = request.POST.get('karbohidrat_malam_3')
    protein_malam_3        = request.POST.get('protein_malam_3')
    lemak_malam_3          = request.POST.get('lemak_malam_3')
    sayuran_a_malam_3      = request.POST.get('sayuran_a_malam_3')
    sayuran_b_malam_3      = request.POST.get('sayuran_b_malam_3')
    total_karbohidrat_3   = request.POST.get('total_karbohidrat_3')
    total_protein_3       = request.POST.get('total_protein_3')
    total_lemak_3         = request.POST.get('total_lemak_3')
    total_kalori_3        = request.POST.get('total_kalori_3')

    berat_buah_pagi_4     = request.POST.get('berat_buah_pagi_4')
    berat_kacang_pagi_4   = request.POST.get('berat_kacang_pagi_4')
    berat_skim_susu_pagi_4= request.POST.get('berat_skim_susu_pagi_4')
    berat_karbo_pagi_4    = request.POST.get('berat_karbo_pagi_4')
    berat_protein_pagi_4  = request.POST.get('berat_protein_pagi_4')
    berat_lemak_pagi_4    = request.POST.get('berat_lemak_pagi_4')
    berat_buah_siang_4    = request.POST.get('berat_buah_siang_4')
    berat_kacang_siang_4   = request.POST.get('berat_kacang_siang_4')
    berat_skim_susu_siang_4= request.POST.get('berat_skim_susu_siang_4')
    berat_karbo_siang_4    = request.POST.get('berat_karbo_siang_4')
    berat_protein_siang_4  = request.POST.get('berat_protein_siang_4')
    berat_lemak_siang_4    = request.POST.get('berat_lemak_siang_4')
    berat_buah_malam_4     = request.POST.get('berat_buah_malam_4')
    berat_kacang_malam_4   = request.POST.get('berat_kacang_malam_4')
    berat_skim_susu_malam_4= request.POST.get('berat_skim_susu_malam_4')
    berat_karbo_malam_4    = request.POST.get('berat_karbo_malam_4')
    berat_protein_malam_4  = request.POST.get('berat_protein_malam_4')
    berat_lemak_malam_4    = request.POST.get('berat_lemak_malam_4')
    buah_pagi_4            = request.POST.get('buah_pagi_4')
    kacang_pagi_4          = request.POST.get('kacang_pagi_4')
    skim_susu_pagi_4       = request.POST.get('skim_susu_pagi_4')
    karbohidrat_pagi_4     = request.POST.get('karbohidrat_pagi_4')
    protein_pagi_4         = request.POST.get('protein_pagi_4')
    lemak_pagi_4           = request.POST.get('lemak_pagi_4')
    sayuran_a_pagi_4       = request.POST.get('sayuran_a_pagi_4')
    sayuran_b_pagi_4       = request.POST.get('sayuran_b_pagi_4')
    buah_siang_4           = request.POST.get('buah_siang_4')
    kacang_siang_4         = request.POST.get('kacang_siang_4')
    skim_susu_siang_4      = request.POST.get('skim_susu_siang_4')
    karbohidrat_siang_4    = request.POST.get('karbohidrat_siang_4')
    protein_siang_4        = request.POST.get('protein_siang_4')
    lemak_siang_4          = request.POST.get('lemak_siang_4')
    sayuran_a_siang_4      = request.POST.get('sayuran_a_siang_4')
    sayuran_b_siang_4      = request.POST.get('sayuran_b_siang_4')
    buah_malam_4           = request.POST.get('buah_malam_4')
    kacang_malam_4         = request.POST.get('kacang_malam_4')
    skim_susu_malam_4      = request.POST.get('skim_susu_malam_4')
    karbohidrat_malam_4    = request.POST.get('karbohidrat_malam_4')
    protein_malam_4        = request.POST.get('protein_malam_4')
    lemak_malam_4          = request.POST.get('lemak_malam_4')
    sayuran_a_malam_4      = request.POST.get('sayuran_a_malam_4')
    sayuran_b_malam_4      = request.POST.get('sayuran_b_malam_4')
    total_karbohidrat_4   = request.POST.get('total_karbohidrat_4')
    total_protein_4       = request.POST.get('total_protein_4')
    total_lemak_4         = request.POST.get('total_lemak_4')
    total_kalori_4        = request.POST.get('total_kalori_4')

    berat_buah_pagi_5     = request.POST.get('berat_buah_pagi_5')
    berat_kacang_pagi_5   = request.POST.get('berat_kacang_pagi_5')
    berat_skim_susu_pagi_5= request.POST.get('berat_skim_susu_pagi_5')
    berat_karbo_pagi_5    = request.POST.get('berat_karbo_pagi_5')
    berat_protein_pagi_5  = request.POST.get('berat_protein_pagi_5')
    berat_lemak_pagi_5    = request.POST.get('berat_lemak_pagi_5')
    berat_buah_siang_5    = request.POST.get('berat_buah_siang_5')
    berat_kacang_siang_5   = request.POST.get('berat_kacang_siang_5')
    berat_skim_susu_siang_5= request.POST.get('berat_skim_susu_siang_5')
    berat_karbo_siang_5    = request.POST.get('berat_karbo_siang_5')
    berat_protein_siang_5  = request.POST.get('berat_protein_siang_5')
    berat_lemak_siang_5    = request.POST.get('berat_lemak_siang_5')
    berat_buah_malam_5     = request.POST.get('berat_buah_malam_5')
    berat_kacang_malam_5   = request.POST.get('berat_kacang_malam_5')
    berat_skim_susu_malam_5= request.POST.get('berat_skim_susu_malam_5')
    berat_karbo_malam_5    = request.POST.get('berat_karbo_malam_5')
    berat_protein_malam_5  = request.POST.get('berat_protein_malam_5')
    berat_lemak_malam_5    = request.POST.get('berat_lemak_malam_5')
    buah_pagi_5            = request.POST.get('buah_pagi_5')
    kacang_pagi_5          = request.POST.get('kacang_pagi_5')
    skim_susu_pagi_5       = request.POST.get('skim_susu_pagi_5')
    karbohidrat_pagi_5     = request.POST.get('karbohidrat_pagi_5')
    protein_pagi_5         = request.POST.get('protein_pagi_5')
    lemak_pagi_5           = request.POST.get('lemak_pagi_5')
    sayuran_a_pagi_5       = request.POST.get('sayuran_a_pagi_5')
    sayuran_b_pagi_5       = request.POST.get('sayuran_b_pagi_5')
    buah_siang_5           = request.POST.get('buah_siang_5')
    kacang_siang_5         = request.POST.get('kacang_siang_5')
    skim_susu_siang_5      = request.POST.get('skim_susu_siang_5')
    karbohidrat_siang_5    = request.POST.get('karbohidrat_siang_5')
    protein_siang_5        = request.POST.get('protein_siang_5')
    lemak_siang_5          = request.POST.get('lemak_siang_5')
    sayuran_a_siang_5      = request.POST.get('sayuran_a_siang_5')
    sayuran_b_siang_5      = request.POST.get('sayuran_b_siang_5')
    buah_malam_5           = request.POST.get('buah_malam_5')
    kacang_malam_5         = request.POST.get('kacang_malam_5')
    skim_susu_malam_5      = request.POST.get('skim_susu_malam_5')
    karbohidrat_malam_5    = request.POST.get('karbohidrat_malam_5')
    protein_malam_5        = request.POST.get('protein_malam_5')
    lemak_malam_5          = request.POST.get('lemak_malam_5')
    sayuran_a_malam_5      = request.POST.get('sayuran_a_malam_5')
    sayuran_b_malam_5      = request.POST.get('sayuran_b_malam_5')
    total_karbohidrat_5   = request.POST.get('total_karbohidrat_5')
    total_protein_5       = request.POST.get('total_protein_5')
    total_lemak_5         = request.POST.get('total_lemak_5')
    total_kalori_5        = request.POST.get('total_kalori_5')

    nama_diet             = request.POST.get('nama_diet')
    deskripsi_diet        = request.POST.get('deskripsi_diet')

    data_personal = {
        'nama'          : nama,
        'jenis_kelamin' : jenis_kelamin,
        'berat_badan'   : berat_badan,
        'tinggi_badan'  : tinggi_badan,
        'usia'          : usia,
        'tingkat_aktivitas' : tingkat_aktivitas,
        'penyakit_penyerta' : penyakit_penyerta,
        'makanan_tidak_suka': makanan_tidak_suka,
        'alergi'            : alergi,
        'kategori_harga'    : kategori_harga,
      }
    
    data_gizi_harian = {
        'bmi' : bmi,
        'bmi_2' : bmi_2,
        'total_kalori'      : total_kalori,
        'total_karbohidrat' : total_karbohidrat,
        'total_protein'     : total_protein,
        'total_lemak'       : total_lemak,
      }
    
    menu_1 = {
      'berat_buah_pagi'       : berat_buah_pagi_1,
      'berat_kacang_pagi'     : berat_kacang_pagi_1,
      'berat_skim_susu_pagi'  : berat_skim_susu_pagi_1,
      'berat_karbo_pagi'    : berat_karbo_pagi_1,
      'berat_protein_pagi'  : berat_protein_pagi_1,
      'berat_lemak_pagi'    : berat_lemak_pagi_1,
      'kacang_pagi'    : kacang_pagi_1,
      'buah_pagi'      : buah_pagi_1,
      'skim_susu_pagi' : skim_susu_pagi_1,
      'sayuran_a_pagi' : sayuran_a_pagi_1,
      'sayuran_b_pagi' : sayuran_b_pagi_1,
      'karbohidrat_pagi': karbohidrat_pagi_1,
      'protein_pagi'   : protein_pagi_1,
      'lemak_pagi'     : lemak_pagi_1,
      'berat_buah_siang'       : berat_buah_siang_1,
      'berat_kacang_siang'     : berat_kacang_siang_1,
      'berat_skim_susu_siang'  : berat_skim_susu_siang_1,
      'berat_karbo_siang'    : berat_karbo_siang_1,
      'berat_protein_siang'  : berat_protein_siang_1,
      'berat_lemak_siang'    : berat_lemak_siang_1,
      'kacang_siang'    : kacang_siang_1,
      'buah_siang'      : buah_siang_1,
      'skim_susu_siang' : skim_susu_siang_1,
      'sayuran_a_siang' : sayuran_a_siang_1,
      'sayuran_b_siang' : sayuran_b_siang_1,
      'karbohidrat_siang': karbohidrat_siang_1,
      'protein_siang'   : protein_siang_1,
      'lemak_siang'     : lemak_siang_1,
      'berat_buah_malam'       : berat_buah_malam_1,
      'berat_kacang_malam'     : berat_kacang_malam_1,
      'berat_skim_susu_malam'  : berat_skim_susu_malam_1,
      'berat_karbo_malam'    : berat_karbo_malam_1,
      'berat_protein_malam'  : berat_protein_malam_1,
      'berat_lemak_malam'    : berat_lemak_malam_1,
      'kacang_malam'    : kacang_malam_1,
      'buah_malam'      : buah_malam_1,
      'skim_susu_malam' : skim_susu_malam_1,
      'sayuran_a_malam' : sayuran_a_malam_1,
      'sayuran_b_malam' : sayuran_b_malam_1,
      'karbohidrat_malam': karbohidrat_malam_1,
      'protein_malam'   : protein_malam_1,
      'lemak_malam'     : lemak_malam_1,
      'total_karbo'     : total_karbohidrat_1,
      'total_protein'   : total_protein_1,
      'total_lemak'     : total_lemak_1,
      'total_kalori'    : total_kalori_1,
    }
    menu_2 = {
      'berat_buah_pagi'       : berat_buah_pagi_2,
      'berat_kacang_pagi'     : berat_kacang_pagi_2,
      'berat_skim_susu_pagi'  : berat_skim_susu_pagi_2,
      'berat_karbo_pagi'    : berat_karbo_pagi_2,
      'berat_protein_pagi'  : berat_protein_pagi_2,
      'berat_lemak_pagi'    : berat_lemak_pagi_2,
      'kacang_pagi'    : kacang_pagi_2,
      'buah_pagi'      : buah_pagi_2,
      'skim_susu_pagi' : skim_susu_pagi_2,
      'sayuran_a_pagi' : sayuran_a_pagi_2,
      'sayuran_b_pagi' : sayuran_b_pagi_2,
      'karbohidrat_pagi': karbohidrat_pagi_2,
      'protein_pagi'   : protein_pagi_2,
      'lemak_pagi'     : lemak_pagi_2,
      'berat_buah_siang'       : berat_buah_siang_2,
      'berat_kacang_siang'     : berat_kacang_siang_2,
      'berat_skim_susu_siang'  : berat_skim_susu_siang_2,
      'berat_karbo_siang'    : berat_karbo_siang_2,
      'berat_protein_siang'  : berat_protein_siang_2,
      'berat_lemak_siang'    : berat_lemak_siang_2,
      'kacang_siang'    : kacang_siang_2,
      'buah_siang'      : buah_siang_2,
      'skim_susu_siang' : skim_susu_siang_2,
      'sayuran_a_siang' : sayuran_a_siang_2,
      'sayuran_b_siang' : sayuran_b_siang_2,
      'karbohidrat_siang': karbohidrat_siang_2,
      'protein_siang'   : protein_siang_2,
      'lemak_siang'     : lemak_siang_2,
      'berat_buah_malam'       : berat_buah_malam_2,
      'berat_kacang_malam'     : berat_kacang_malam_2,
      'berat_skim_susu_malam'  : berat_skim_susu_malam_2,
      'berat_karbo_malam'    : berat_karbo_malam_2,
      'berat_protein_malam'  : berat_protein_malam_2,
      'berat_lemak_malam'    : berat_lemak_malam_2,
      'kacang_malam'    : kacang_malam_2,
      'buah_malam'      : buah_malam_2,
      'skim_susu_malam' : skim_susu_malam_2,
      'sayuran_a_malam' : sayuran_a_malam_2,
      'sayuran_b_malam' : sayuran_b_malam_2,
      'karbohidrat_malam': karbohidrat_malam_2,
      'protein_malam'   : protein_malam_2,
      'lemak_malam'     : lemak_malam_2,
      'total_karbo'     : total_karbohidrat_2,
      'total_protein'   : total_protein_2,
      'total_lemak'     : total_lemak_2,
      'total_kalori'    : total_kalori_2,
    }
    menu_3 = {
      'berat_buah_pagi'       : berat_buah_pagi_3,
      'berat_kacang_pagi'     : berat_kacang_pagi_3,
      'berat_skim_susu_pagi'  : berat_skim_susu_pagi_3,
      'berat_karbo_pagi'    : berat_karbo_pagi_3,
      'berat_protein_pagi'  : berat_protein_pagi_3,
      'berat_lemak_pagi'    : berat_lemak_pagi_3,
      'kacang_pagi'    : kacang_pagi_3,
      'buah_pagi'      : buah_pagi_3,
      'skim_susu_pagi' : skim_susu_pagi_3,
      'sayuran_a_pagi' : sayuran_a_pagi_3,
      'sayuran_b_pagi' : sayuran_b_pagi_3,
      'karbohidrat_pagi': karbohidrat_pagi_3,
      'protein_pagi'   : protein_pagi_3,
      'lemak_pagi'     : lemak_pagi_3,
      'berat_buah_siang'       : berat_buah_siang_3,
      'berat_kacang_siang'     : berat_kacang_siang_3,
      'berat_skim_susu_siang'  : berat_skim_susu_siang_3,
      'berat_karbo_siang'    : berat_karbo_siang_3,
      'berat_protein_siang'  : berat_protein_siang_3,
      'berat_lemak_siang'    : berat_lemak_siang_3,
      'kacang_siang'    : kacang_siang_3,
      'buah_siang'      : buah_siang_3,
      'skim_susu_siang' : skim_susu_siang_3,
      'sayuran_a_siang' : sayuran_a_siang_3,
      'sayuran_b_siang' : sayuran_b_siang_3,
      'karbohidrat_siang': karbohidrat_siang_3,
      'protein_siang'   : protein_siang_3,
      'lemak_siang'     : lemak_siang_3,
      'berat_buah_malam'       : berat_buah_malam_3,
      'berat_kacang_malam'     : berat_kacang_malam_3,
      'berat_skim_susu_malam'  : berat_skim_susu_malam_3,
      'berat_karbo_malam'    : berat_karbo_malam_3,
      'berat_protein_malam'  : berat_protein_malam_3,
      'berat_lemak_malam'    : berat_lemak_malam_3,
      'kacang_malam'    : kacang_malam_3,
      'buah_malam'      : buah_malam_3,
      'skim_susu_malam' : skim_susu_malam_3,
      'sayuran_a_malam' : sayuran_a_malam_3,
      'sayuran_b_malam' : sayuran_b_malam_3,
      'karbohidrat_malam': karbohidrat_malam_3,
      'protein_malam'   : protein_malam_3,
      'lemak_malam'     : lemak_malam_3,
      'total_karbo'     : total_karbohidrat_3,
      'total_protein'   : total_protein_3,
      'total_lemak'     : total_lemak_3,
      'total_kalori'    : total_kalori_3,
    }

    menu_4 = {
      'berat_buah_pagi'       : berat_buah_pagi_4,
      'berat_kacang_pagi'     : berat_kacang_pagi_4,
      'berat_skim_susu_pagi'  : berat_skim_susu_pagi_4,
      'berat_karbo_pagi'    : berat_karbo_pagi_4,
      'berat_protein_pagi'  : berat_protein_pagi_4,
      'berat_lemak_pagi'    : berat_lemak_pagi_4,
      'kacang_pagi'    : kacang_pagi_4,
      'buah_pagi'      : buah_pagi_4,
      'skim_susu_pagi' : skim_susu_pagi_4,
      'sayuran_a_pagi' : sayuran_a_pagi_4,
      'sayuran_b_pagi' : sayuran_b_pagi_4,
      'karbohidrat_pagi': karbohidrat_pagi_4,
      'protein_pagi'   : protein_pagi_4,
      'lemak_pagi'     : lemak_pagi_4,
      'berat_buah_siang'       : berat_buah_siang_4,
      'berat_kacang_siang'     : berat_kacang_siang_4,
      'berat_skim_susu_siang'  : berat_skim_susu_siang_4,
      'berat_karbo_siang'    : berat_karbo_siang_4,
      'berat_protein_siang'  : berat_protein_siang_4,
      'berat_lemak_siang'    : berat_lemak_siang_4,
      'kacang_siang'    : kacang_siang_4,
      'buah_siang'      : buah_siang_4,
      'skim_susu_siang' : skim_susu_siang_4,
      'sayuran_a_siang' : sayuran_a_siang_4,
      'sayuran_b_siang' : sayuran_b_siang_4,
      'karbohidrat_siang': karbohidrat_siang_4,
      'protein_siang'   : protein_siang_4,
      'lemak_siang'     : lemak_siang_4,
      'berat_buah_malam'       : berat_buah_malam_4,
      'berat_kacang_malam'     : berat_kacang_malam_4,
      'berat_skim_susu_malam'  : berat_skim_susu_malam_4,
      'berat_karbo_malam'    : berat_karbo_malam_4,
      'berat_protein_malam'  : berat_protein_malam_4,
      'berat_lemak_malam'    : berat_lemak_malam_4,
      'kacang_malam'    : kacang_malam_4,
      'buah_malam'      : buah_malam_4,
      'skim_susu_malam' : skim_susu_malam_4,
      'sayuran_a_malam' : sayuran_a_malam_4,
      'sayuran_b_malam' : sayuran_b_malam_4,
      'karbohidrat_malam': karbohidrat_malam_4,
      'protein_malam'   : protein_malam_4,
      'lemak_malam'     : lemak_malam_4,
      'total_karbo'     : total_karbohidrat_4,
      'total_protein'   : total_protein_4,
      'total_lemak'     : total_lemak_4,
      'total_kalori'    : total_kalori_4,
    }

    menu_5 = {
            'berat_buah_pagi'       : berat_buah_pagi_5,
      'berat_kacang_pagi'     : berat_kacang_pagi_5,
      'berat_skim_susu_pagi'  : berat_skim_susu_pagi_5,
      'berat_karbo_pagi'    : berat_karbo_pagi_5,
      'berat_protein_pagi'  : berat_protein_pagi_5,
      'berat_lemak_pagi'    : berat_lemak_pagi_5,
      'kacang_pagi'    : kacang_pagi_5,
      'buah_pagi'      : buah_pagi_5,
      'skim_susu_pagi' : skim_susu_pagi_5,
      'sayuran_a_pagi' : sayuran_a_pagi_5,
      'sayuran_b_pagi' : sayuran_b_pagi_5,
      'karbohidrat_pagi': karbohidrat_pagi_5,
      'protein_pagi'   : protein_pagi_5,
      'lemak_pagi'     : lemak_pagi_5,
      'berat_buah_siang'       : berat_buah_siang_5,
      'berat_kacang_siang'     : berat_kacang_siang_5,
      'berat_skim_susu_siang'  : berat_skim_susu_siang_5,
      'berat_karbo_siang'    : berat_karbo_siang_5,
      'berat_protein_siang'  : berat_protein_siang_5,
      'berat_lemak_siang'    : berat_lemak_siang_5,
      'kacang_siang'    : kacang_siang_5,
      'buah_siang'      : buah_siang_5,
      'skim_susu_siang' : skim_susu_siang_5,
      'sayuran_a_siang' : sayuran_a_siang_5,
      'sayuran_b_siang' : sayuran_b_siang_5,
      'karbohidrat_siang': karbohidrat_siang_5,
      'protein_siang'   : protein_siang_5,
      'lemak_siang'     : lemak_siang_5,
      'berat_buah_malam'       : berat_buah_malam_5,
      'berat_kacang_malam'     : berat_kacang_malam_5,
      'berat_skim_susu_malam'  : berat_skim_susu_malam_5,
      'berat_karbo_malam'    : berat_karbo_malam_5,
      'berat_protein_malam'  : berat_protein_malam_5,
      'berat_lemak_malam'    : berat_lemak_malam_5,
      'kacang_malam'    : kacang_malam_5,
      'buah_malam'      : buah_malam_5,
      'skim_susu_malam' : skim_susu_malam_5,
      'sayuran_a_malam' : sayuran_a_malam_5,
      'sayuran_b_malam' : sayuran_b_malam_5,
      'karbohidrat_malam': karbohidrat_malam_5,
      'protein_malam'   : protein_malam_5,
      'lemak_malam'     : lemak_malam_5,
      'total_karbo'     : total_karbohidrat_5,
      'total_protein'   : total_protein_5,
      'total_lemak'     : total_lemak_5,
      'total_kalori'    : total_kalori_5,
    }

    jenis_diet = {
        'nama_diet' : nama_diet,
        'deskripsi_diet' : deskripsi_diet,
      }
    
    template_path = 'pdftemplate.html'
    template = get_template(template_path)
    context = {'data_personal': data_personal, 'data_gizi_harian' : data_gizi_harian, 'jenis_diet' : jenis_diet, 'menu_1' : menu_1, 'menu_2' : menu_2, 'menu_3' : menu_3, 'menu_4' : menu_4, 'menu_5' : menu_5}
    html = template.render(context)

    namafile = f"Diet_{nama}.pdf"
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="{namafile}"'

    # Buat dokumen PDF dari HTML
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    # Jika berhasil membuat PDF, kembalikan response
    if pisa_status.err:
        return HttpResponse('Gagal membuat PDF: %s' % pisa_status.err)
    return response
    
  return render(request, 'inputpage.html')