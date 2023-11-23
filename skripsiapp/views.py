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
        penyakit_penyerta_2 = 'Kolesterol dalam darah yang tinggi'
        kode_penyakit = 'K02'
      elif penyakit_penyerta == '2':
        penyakit_penyerta_2 = 'Komplikasi pembuluh darah'
        kode_penyakit = 'K03'
      elif penyakit_penyerta == '3':
        penyakit_penyerta_2 = 'lama menderita lebih dari 15 tahun'
        kode_penyakit = 'K04'
      elif penyakit_penyerta == '4':
        penyakit_penyerta_2 = 'Stroke'
        kode_penyakit = 'K05'
      elif penyakit_penyerta == '5':
        penyakit_penyerta_2 = 'Jantung Koroner'
        kode_penyakit = 'K05'
      elif penyakit_penyerta == '6':
        penyakit_penyerta_2 = 'Infark Jantung'
        kode_penyakit = 'K05'
      elif penyakit_penyerta == '7':
        penyakit_penyerta_2 = 'Penyakit pembuluh arteri perifer oklusif'
        kode_penyakit = 'K05'
      elif penyakit_penyerta == '8':
        penyakit_penyerta_2 = 'Gangren'
        kode_penyakit = 'K06'
      else:
        penyakit_penyerta_2 = '-'
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
        total_protein_actual = round(kalori_harian_final * 0.2 / 4, 3)
        total_lemak_actual   = round(kalori_harian_final * 0.2 / 9, 3)
        total_karbo   = round(total_kalori * 0.6 / 4, 3)
        total_protein = round(total_kalori * 0.2 / 4, 3)
        total_lemak   = round(total_kalori * 0.2 / 9, 3)
      else:
        total_karbo_actual   = round(kalori_harian_final * 0.68 / 4, 3)
        total_protein_actual = round(kalori_harian_final * 0.12 / 4, 3)
        total_lemak_actual   = round(kalori_harian_final * 0.2 / 9, 3)
        total_karbo   = round(total_kalori * 0.68 / 4, 3)
        total_protein = round(total_kalori * 0.12 / 4, 3)
        total_lemak   = round(total_kalori * 0.2 / 9, 3)
      #Menghitung total zat gizi yang diperlukan 

      data_gizi_harian = {
        'bmi' : round(bmi, 3),
        'bmi_2' : bmi_2,
        'total_kalori'      : kalori_harian_final,
        'total_karbohidrat' : total_karbo_actual,
        'total_protein'     : total_protein_actual,
        'total_lemak'       : total_lemak_actual
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

      #data perkategori
      data_buah      = data_makanan[data_makanan['kategori'] == 'Buah']
      data_kacang    = data_makanan[data_makanan['kategori'] == 'kacang']
      data_skim_susu = data_makanan[data_makanan['kategori'] == 'Skim Susu']

      data_karbohidrat  = data_makanan[data_makanan['kategori'] == 'Karbohidrat']
      data_lemak        = data_makanan[(data_makanan['kategori'] == 'Lemak') | (data_makanan['kategori'] == 'Lemak Hewani')]
      data_sayuran_a    = data_makanan[data_makanan['kategori'] == 'Sayuran A']
      data_sayuran_b    = data_makanan[data_makanan['kategori'] == 'Sayuran B']
      data_protein      = data_makanan[(data_makanan['kategori'] == 'Protein Nabati') | (data_makanan['kategori'] == 'Protein Hewani')]
      
      if kategori_harga != "":
        if kategori_harga == "1":
          data_buah_1 = data_buah[data_buah['harga'] < 3600]
          if len(data_buah_1) < 7:
            data_buah_1 = data_buah[data_buah['harga'] < 8000]
          data_kacang_1 = data_kacang[data_kacang['harga'] < 3600]
          if len(data_kacang_1) < 6:
            data_kacang_1 = data_kacang[data_kacang['harga'] < 8000]
          data_karbohidrat_1 = data_karbohidrat[data_karbohidrat['harga'] < 3600]
          if len(data_karbohidrat_1) < 7:
            data_karbohidrat_1 = data_karbohidrat[data_karbohidrat['harga'] < 8000]  
          data_lemak_1 = data_lemak[data_lemak['harga'] < 3600]
          if len(data_lemak_1) < 7:
            data_lemak_1 = data_lemak[data_lemak['harga'] < 8000]  
            if len(data_lemak_1) < 7:
              data_lemak_1 = data_lemak                              
          data_sayuran_a_1 = data_sayuran_a[data_sayuran_a['harga'] < 3600]
          if len(data_sayuran_a_1) < 7:
            data_sayuran_a_1 = data_sayuran_a[data_sayuran_a['harga'] < 8000]
          data_sayuran_b_1 = data_sayuran_b[data_sayuran_b['harga'] < 3600]
          if len(data_sayuran_b_1) < 7:
            data_sayuran_b_1 = data_sayuran_b[data_sayuran_b['harga'] < 8000]
          data_protein_1 = data_protein[data_protein['harga'] < 3600]
          if len(data_protein_1) < 7:
            data_protein_1 = data_protein[data_protein['harga'] < 8000]
        elif kategori_harga == "2":
          data_buah_1 = data_buah[(data_buah['harga'] >= 3600) & (data_buah['harga'] <= 8000)]
          if len(data_buah_1) < 7:
            data_buah_1 = data_buah[data_buah['harga'] <= 8000]
          data_kacang_1 = data_kacang[(data_kacang['harga'] >= 3600) & (data_kacang['harga'] <= 8000)]
          if len(data_kacang_1) < 6:
            data_kacang_1 = data_kacang[data_kacang['harga'] <= 8000]
          data_karbohidrat_1 = data_karbohidrat[(data_karbohidrat['harga'] >= 3600) & (data_karbohidrat['harga'] <= 8000)]
          if len(data_karbohidrat_1) < 7:
            data_karbohidrat_1 = data_karbohidrat[data_karbohidrat['harga'] < 8000]  
          data_lemak_1 = data_lemak[(data_lemak['harga'] >= 3600) & (data_lemak['harga'] <= 8000)]
          if len(data_lemak_1) < 7:
            data_lemak_1 = data_lemak[data_lemak['harga'] <= 8000]
            if len(data_lemak_1) < 7:
              data_lemak_1 = data_lemak                   
          data_sayuran_a_1 = data_sayuran_a[(data_sayuran_a['harga'] >= 3600) & (data_sayuran_a['harga'] <= 8000)]
          if len(data_sayuran_a_1) < 7:
            data_sayuran_a_1 = data_sayuran_a[data_sayuran_a['harga'] <= 8000]
          data_sayuran_b_1 = data_sayuran_b[(data_sayuran_b['harga'] >= 3600) & (data_sayuran_b['harga'] <= 8000)]
          if len(data_sayuran_b_1) < 7:
            data_sayuran_b_1 = data_sayuran_b[data_sayuran_b['harga'] < 8000]
          data_protein_1 = data_protein[(data_protein['harga'] >= 3600) & (data_protein['harga'] <= 8000)]
          if len(data_protein_1) < 7:
            data_protein_1 = data_protein[data_protein['harga'] <= 8000]
        else:
          data_buah_1 = data_buah[data_buah['harga'] > 8000]
          if len(data_buah_1) < 7:
            data_buah_1 = data_buah[data_buah['harga'] > 3600]
            if len(data_buah_1) < 7:
              data_buah_1 = data_buah[data_buah['harga'] > 0]
          data_kacang_1 = data_kacang[data_kacang['harga'] > 8000]
          if len(data_kacang_1) < 7:
            data_kacang_1 = data_kacang[data_kacang['harga'] > 3600]
            if len(data_kacang_1) < 7:
              data_kacang_1 = data_kacang[data_kacang['harga'] > 0]
          data_karbohidrat_1 = data_karbohidrat[data_karbohidrat['harga'] > 8000]
          if len(data_karbohidrat_1) < 7:
            data_karbohidrat_1 = data_karbohidrat[data_karbohidrat['harga'] > 3600]  
            if len(data_karbohidrat_1) < 7:
              data_karbohidrat_1 = data_karbohidrat[data_karbohidrat['harga'] > 0]  
          data_lemak_1 = data_lemak[data_lemak['harga'] > 8000]
          if len(data_lemak_1) < 7:
            data_lemak_1 = data_lemak[data_lemak['harga'] > 3600]    
            if len(data_lemak_1) < 7:
              data_lemak_1 = data_lemak[data_lemak['harga'] > 0]
          data_sayuran_a_1 = data_sayuran_a[data_sayuran_a['harga'] > 8000]
          if len(data_sayuran_a_1) < 7:
            data_sayuran_a_1 = data_sayuran_a[data_sayuran_a['harga'] > 3600]
            if len(data_sayuran_a_1) < 7:
              data_sayuran_a_1 = data_sayuran_a[data_sayuran_a['harga'] > 0]
          data_sayuran_b_1 = data_sayuran_b[data_sayuran_b['harga'] > 8000]
          if len(data_sayuran_b_1) < 7:
            data_sayuran_b_1 = data_sayuran_b[data_sayuran_b['harga'] > 3600]
            if len(data_sayuran_b_1) < 7:
              data_sayuran_b_1 = data_sayuran_b[data_sayuran_b['harga'] > 0]
          data_protein_1 = data_protein[data_protein['harga'] > 8000]
          if len(data_protein_1) < 7:
            data_protein_1 = data_protein[data_protein['harga'] > 3600]
            if len(data_protein_1) < 7:
              data_protein_1 = data_protein[data_protein['harga'] > 0]
        data_karbohidrat = data_karbohidrat_1
        data_buah        = data_buah_1
        data_protein     = data_protein_1
        data_lemak       = data_lemak_1
        data_kacang      = data_kacang_1
        data_sayuran_a   = data_sayuran_a_1
        data_sayuran_b   = data_sayuran_b_1
        data_karbohidrat_1 = ""
        data_buah_1        = ""
        data_protein_1     = ""
        data_lemak_1       = ""
        data_kacang_1      = ""
        data_sayuran_a_1   = ""
        data_sayuran_b_1   = ""
        # data_kacang_1      = ""

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

      #Menu 1
      total_kalori_1 = 0

      while total_kalori_1 < kalori_harian_final * 0.9:
        karbohidrat_index    = random.randint(0, data_karbohidrat.shape[0] - 1)
        protein_index        = random.randint(0, data_protein.shape[0] - 1)
        lemak_index          = random.randint(0, data_lemak.shape[0] - 1)
        sayuran_a_index      = random.randint(0, data_sayuran_a.shape[0] - 1)
        sayuran_b_index      = random.randint(0, data_sayuran_b.shape[0] - 1)
        kacang_index         = random.randint(0, data_kacang.shape[0] - 1)
        buah_index           = random.randint(0, data_buah.shape[0] - 1)
        skim_susu_index      = random.randint(0, data_skim_susu.shape[0] - 1)

        # Ambil baris secara acak dari DataFrame
        karbohidrat_1  = data_karbohidrat.iloc[karbohidrat_index]
        protein_1      = data_protein.iloc[protein_index]
        lemak_1        = data_lemak.iloc[lemak_index]
        sayuran_a_1    = data_sayuran_a.iloc[sayuran_a_index]
        sayuran_b_1    = data_sayuran_b.iloc[sayuran_b_index]
        buah_1         = data_buah.iloc[buah_index]
        kacang_1       = data_kacang.iloc[kacang_index]
        skim_susu_1    = data_skim_susu.iloc[skim_susu_index]

        #camilan menu 1
        #koefisien matriks
        A = [[kacang_1['karbohidrat']/100, buah_1['karbohidrat']/100, skim_susu_1['karbohidrat']/100],
            [kacang_1['protein']/100, buah_1['protein']/100, skim_susu_1['protein']/100],
            [kacang_1['lemak']/100, buah_1['lemak']/100, skim_susu_1['lemak']/100]]
        b = [karbo_camilan, protein_camilan, lemak_camilan]
        c = [-1, -1, -1]

        # Menentukan batasan-batasan variabel
        x2_bounds = (1, None)
        y2_bounds = (1, 125)
        z2_bounds = (0, 50)

        # Menyelesaikan permasalahan dengan metode simplex
        result = linprog(c, A_ub=A, b_ub=b, bounds=[x2_bounds, y2_bounds, z2_bounds])
        berat_kacang_1    = round(result.x[0],3)
        berat_buah_1      = round(result.x[1],3)
        berat_skim_susu_1 = round(result.x[2],3)

        #makan pagi menu 1
        A = [[karbohidrat_1['karbohidrat']/100, protein_1['karbohidrat']/100, lemak_1['karbohidrat']/100],
            [karbohidrat_1['protein']/100, protein_1['protein']/100, lemak_1['protein']/100],
            [karbohidrat_1['lemak']/100, protein_1['lemak']/100, lemak_1['lemak']/100]]
        b1 = [karbo_pagi - sayuran_a_1['karbohidrat'] - sayuran_b_1['karbohidrat']/4, protein_pagi - sayuran_a_1['protein'] - sayuran_b_1['protein']/4, lemak_pagi - sayuran_a_1['lemak'] - sayuran_b_1['lemak']/4]
        b2 = [karbo_siang - sayuran_a_1['karbohidrat'] - sayuran_b_1['karbohidrat']/2, protein_siang - sayuran_a_1['protein'] - sayuran_b_1['protein']/2, lemak_siang - sayuran_a_1['lemak'] - sayuran_b_1['lemak']/2]
        c = [-1, -1, -1]

        # Menentukan batasan-batasan variabel
        x3_bounds = (1, karbo_siang*2)
        if kalori_harian_final < 1500:
          y3_bounds = (15, None)
        else:
          y3_bounds = (20, None)
        z3_bounds = (0, None)

        # Menyelesaikan permasalahan dengan metode simplex
        max_iterasi = 100 

        for _ in range(max_iterasi):
            result = linprog(c, A_ub=A, b_ub=b1, bounds=[x3_bounds, y3_bounds, z3_bounds])
            if result is not None:
                break

        berat_karbo_pagi_1   = round(result.x[0],3)
        berat_protein_pagi_1 = round(result.x[1],3)
        berat_lemak_pagi_1   = round(result.x[2],3)

        #makan siang malam menu 1
        result2 = linprog(c, A_ub=A, b_ub=b2, bounds=[x3_bounds, y3_bounds, z3_bounds])
        berat_karbo_siang_1   = round(result2.x[0],3)
        berat_protein_siang_1 = round(result2.x[1],3)
        berat_lemak_siang_1   = round(result2.x[2],3)

        total_karbohidrat_1 = round((karbohidrat_1['karbohidrat'] / 100) * (2 * berat_karbo_siang_1 + berat_karbo_pagi_1) + (protein_1['karbohidrat'] / 100) * (2 * berat_protein_siang_1 + berat_protein_pagi_1) + (lemak_1['karbohidrat'] / 100) * (2 * berat_lemak_siang_1 + berat_lemak_pagi_1) 
        + (3 * sayuran_a_1['karbohidrat']) + (1.25 * sayuran_b_1['karbohidrat'])
        + (buah_1['karbohidrat'] / 100) * (3 * berat_buah_1) + (kacang_1['karbohidrat'] / 100) * (3 * berat_kacang_1) + (skim_susu_1['karbohidrat'] / 100) * (3 * berat_skim_susu_1), 3)

        total_protein_1 = round((karbohidrat_1['protein'] / 100) * (2 * berat_karbo_siang_1 + berat_karbo_pagi_1) + (protein_1['protein'] / 100) * (2 * berat_protein_siang_1 + berat_protein_pagi_1) + (lemak_1['protein'] / 100) * (2 * berat_lemak_siang_1 + berat_lemak_pagi_1) 
        + (3 * sayuran_a_1['protein']) + (1.25 * sayuran_b_1['protein'])
        + (buah_1['protein'] / 100) * (3 * berat_buah_1) + (kacang_1['protein'] / 100) * (3 * berat_kacang_1) + (skim_susu_1['protein'] / 100) * (3 * berat_skim_susu_1), 3)

        total_lemak_1 = round((karbohidrat_1['lemak'] / 100) * (2 * berat_karbo_siang_1 + berat_karbo_pagi_1) + (protein_1['lemak'] / 100) * (2 * berat_protein_siang_1 + berat_protein_pagi_1) + (lemak_1['lemak'] / 100) * (2 * berat_lemak_siang_1 + berat_lemak_pagi_1) 
        + (3 * sayuran_a_1['lemak']) + (1.25 * sayuran_b_1['lemak'])
        + (buah_1['lemak'] / 100) * (3 * berat_buah_1) + (kacang_1['lemak'] / 100) * (3 * berat_kacang_1) + (skim_susu_1['lemak'] / 100) * (3 * berat_skim_susu_1), 3)

        total_kalori_1 = round (total_karbohidrat_1 * 4 + total_protein_1 * 4 + total_lemak_1 * 9 , 3)

      protein_exclude.append(protein_1['id'])
      lemak_exclude.append(lemak_1['id'])
      sayuran_a_exclude.append(sayuran_a_1['id'])
      sayuran_b_exclude.append(sayuran_b_1['id'])
      kacang_exclude.append(kacang_1['id'])
      buah_exclude.append(buah_1['id'])

      #Menu 2

      total_kalori_2 = 0

      while total_kalori_2 < kalori_harian_final * 0.9:

        karbohidrat_index = random.randint(0, data_karbohidrat.shape[0] - 1)
        karbohidrat_2     = data_karbohidrat.iloc[karbohidrat_index]

        filtered_data_protein = data_protein[~data_protein['id'].isin(protein_exclude)]
        protein_index   = random.randint(0, filtered_data_protein.shape[0] - 1)
        protein_2       = filtered_data_protein.iloc[protein_index]

        filtered_data_lemak = data_lemak[~data_lemak['id'].isin(lemak_exclude)]
        lemak_index     = random.randint(0, filtered_data_lemak.shape[0] - 1)
        lemak_2         = filtered_data_lemak.iloc[lemak_index]

        filtered_data_sayuran_a = data_sayuran_a[~data_sayuran_a['id'].isin(sayuran_a_exclude)]
        sayuran_a_index = random.randint(0, filtered_data_sayuran_a.shape[0] - 1)
        sayuran_a_2     = filtered_data_sayuran_a.iloc[sayuran_a_index]

        filtered_data_sayuran_b = data_sayuran_b[~data_sayuran_b['id'].isin(sayuran_b_exclude)]
        sayuran_b_index = random.randint(0, filtered_data_sayuran_b.shape[0] - 1)
        sayuran_b_2     = filtered_data_sayuran_b.iloc[sayuran_b_index]

        filtered_data_kacang = data_kacang[~data_kacang['id'].isin(kacang_exclude)]
        kacang_index    = random.randint(0, filtered_data_kacang.shape[0] - 1)
        kacang_2        = filtered_data_kacang.iloc[kacang_index]
        
        filtered_data_buah = data_buah[~data_buah['id'].isin(buah_exclude)]
        buah_index      = random.randint(0, filtered_data_buah.shape[0] - 1)
        buah_2          = filtered_data_buah.iloc[buah_index]

        skim_susu_index = random.randint(0, data_skim_susu.shape[0] - 1)
        skim_susu_2     = data_skim_susu.iloc[skim_susu_index]

        #camilan menu 2
        #koefisien matriks
        A = [[kacang_2['karbohidrat']/100, buah_2['karbohidrat']/100, skim_susu_2['karbohidrat']/100],
            [kacang_2['protein']/100, buah_2['protein']/100, skim_susu_2['protein']/100],
            [kacang_2['lemak']/100, buah_2['lemak']/100, skim_susu_2['lemak']/100]]
        b = [karbo_camilan, protein_camilan, lemak_camilan]
        c = [-1, -1, -1]

        # Menentukan batasan-batasan variabel
        x2_bounds = (1, None)
        y2_bounds = (1, 125)
        z2_bounds = (0, 50)

        # Menyelesaikan permasalahan dengan metode simplex
        result = linprog(c, A_ub=A, b_ub=b, bounds=[x2_bounds, y2_bounds, z2_bounds])
        berat_kacang_2    = round(result.x[0],3)
        berat_buah_2      = round(result.x[1],3)
        berat_skim_susu_2 = round(result.x[2],3)

        #makan pagi menu 2
        A = [[karbohidrat_2['karbohidrat']/100, protein_2['karbohidrat']/100, lemak_2['karbohidrat']/100],
            [karbohidrat_2['protein']/100, protein_2['protein']/100, lemak_2['protein']/100],
            [karbohidrat_2['lemak']/100, protein_2['lemak']/100, lemak_2['lemak']/100]]
        b1 = [karbo_pagi - sayuran_a_2['karbohidrat'] - sayuran_b_2['karbohidrat']/4, protein_pagi - sayuran_a_2['protein'] - sayuran_b_2['protein']/4, lemak_pagi - sayuran_a_2['lemak'] - sayuran_b_2['lemak']/4]
        b2 = [karbo_siang - sayuran_a_2['karbohidrat'] - sayuran_b_2['karbohidrat']/2, protein_siang - sayuran_a_2['protein'] - sayuran_b_2['protein']/2, lemak_siang - sayuran_a_2['lemak'] - sayuran_b_2['lemak']/2]
        c = [-1, -1, -1]

        # Menentukan batasan-batasan variabel
        x3_bounds = (1, karbo_siang*2)
        if kalori_harian_final < 1500:
          y3_bounds = (15, None)
        else:
          y3_bounds = (20, None)
        z3_bounds = (0, None)

        # Menyelesaikan permasalahan dengan metode simplex
        max_iterasi = 100 

        for _ in range(max_iterasi):
            result = linprog(c, A_ub=A, b_ub=b1, bounds=[x3_bounds, y3_bounds, z3_bounds])
            if result is not None:
                break

        berat_karbo_pagi_2   = round(result.x[0],3)
        berat_protein_pagi_2 = round(result.x[1],3)
        berat_lemak_pagi_2   = round(result.x[2],3)

        #makan siang malam menu 1
        result2 = linprog(c, A_ub=A, b_ub=b2, bounds=[x3_bounds, y3_bounds, z3_bounds])
        berat_karbo_siang_2   = round(result2.x[0],3)
        berat_protein_siang_2 = round(result2.x[1],3)
        berat_lemak_siang_2   = round(result2.x[2],3)

        total_karbohidrat_2 = round((karbohidrat_2['karbohidrat'] / 100) * (2 * berat_karbo_siang_2 + berat_karbo_pagi_2) + (protein_2['karbohidrat'] / 100) * (2 * berat_protein_siang_2 + berat_protein_pagi_2) + (lemak_2['karbohidrat'] / 100) * (2 * berat_lemak_siang_2 + berat_lemak_pagi_2) 
        + (3 * sayuran_a_2['karbohidrat']) + (1.25 * sayuran_b_2['karbohidrat'])
        + (buah_2['karbohidrat'] / 100) * (3 * berat_buah_2) + (kacang_2['karbohidrat'] / 100) * (3 * berat_kacang_2) + (skim_susu_2['karbohidrat'] / 100) * (3 * berat_skim_susu_2), 3)

        total_protein_2 = round((karbohidrat_2['protein'] / 100) * (2 * berat_karbo_siang_2 + berat_karbo_pagi_2) + (protein_2['protein'] / 100) * (2 * berat_protein_siang_2 + berat_protein_pagi_2) + (lemak_2['protein'] / 100) * (2 * berat_lemak_siang_2 + berat_lemak_pagi_2) 
        + (3 * sayuran_a_2['protein']) + (1.25 * sayuran_b_2['protein'])
        + (buah_2['protein'] / 100) * (3 * berat_buah_2) + (kacang_2['protein'] / 100) * (3 * berat_kacang_2) + (skim_susu_2['protein'] / 100) * (3 * berat_skim_susu_2), 3)

        total_lemak_2 = round((karbohidrat_2['lemak'] / 100) * (2 * berat_karbo_siang_2 + berat_karbo_pagi_2) + (protein_2['lemak'] / 100) * (2 * berat_protein_siang_2 + berat_protein_pagi_2) + (lemak_2['lemak'] / 100) * (2 * berat_lemak_siang_2 + berat_lemak_pagi_2) 
        + (3 * sayuran_a_2['lemak']) + (1.25 * sayuran_b_2['lemak'])
        + (buah_2['lemak'] / 100) * (3 * berat_buah_2) + (kacang_2['lemak'] / 100) * (3 * berat_kacang_2) + (skim_susu_2['lemak'] / 100) * (3 * berat_skim_susu_2), 3)

        total_kalori_2 = round (total_karbohidrat_2 * 4 + total_protein_2 * 4 + total_lemak_2 * 9 , 3)

      protein_exclude.append(protein_2['id'])
      lemak_exclude.append(lemak_2['id'])
      sayuran_a_exclude.append(sayuran_a_2['id'])
      sayuran_b_exclude.append(sayuran_b_2['id'])
      kacang_exclude.append(kacang_2['id'])
      buah_exclude.append(buah_2['id'])

      #Menu 3
      total_kalori_3 = 0

      while total_kalori_3 < kalori_harian_final * 0.9:
        karbohidrat_index = random.randint(0, data_karbohidrat.shape[0] - 1)
        karbohidrat_3     = data_karbohidrat.iloc[karbohidrat_index]

        filtered_data_protein = data_protein[~data_protein['id'].isin(protein_exclude)]
        protein_index   = random.randint(0, filtered_data_protein.shape[0] - 1)
        protein_3       = filtered_data_protein.iloc[protein_index]

        filtered_data_lemak = data_lemak[~data_lemak['id'].isin(lemak_exclude)]
        lemak_index     = random.randint(0, filtered_data_lemak.shape[0] - 1)
        lemak_3         = filtered_data_lemak.iloc[lemak_index]

        filtered_data_sayuran_a = data_sayuran_a[~data_sayuran_a['id'].isin(sayuran_a_exclude)]
        sayuran_a_index = random.randint(0, filtered_data_sayuran_a.shape[0] - 1)
        sayuran_a_3     = filtered_data_sayuran_a.iloc[sayuran_a_index]

        filtered_data_sayuran_b = data_sayuran_b[~data_sayuran_b['id'].isin(sayuran_b_exclude)]
        sayuran_b_index = random.randint(0, filtered_data_sayuran_b.shape[0] - 1)
        sayuran_b_3     = filtered_data_sayuran_b.iloc[sayuran_b_index]

        filtered_data_kacang = data_kacang[~data_kacang['id'].isin(kacang_exclude)]
        kacang_index    = random.randint(0, filtered_data_kacang.shape[0] - 1)
        kacang_3        = filtered_data_kacang.iloc[kacang_index]
        
        filtered_data_buah = data_buah[~data_buah['id'].isin(buah_exclude)]
        buah_index      = random.randint(0, filtered_data_buah.shape[0] - 1)
        buah_3          = filtered_data_buah.iloc[buah_index]

        skim_susu_index = random.randint(0, data_skim_susu.shape[0] - 1)
        skim_susu_3     = data_skim_susu.iloc[skim_susu_index]
        #camilan menu 3
        #koefisien matriks
        A = [[kacang_3['karbohidrat']/100, buah_3['karbohidrat']/100, skim_susu_3['karbohidrat']/100],
            [kacang_3['protein']/100, buah_3['protein']/100, skim_susu_3['protein']/100],
            [kacang_3['lemak']/100, buah_3['lemak']/100, skim_susu_3['lemak']/100]]
        b = [karbo_camilan, protein_camilan, lemak_camilan]
        c = [-1, -1, -1]

        # Menentukan batasan-batasan variabel
        x2_bounds = (1, None)
        y2_bounds = (1, 125)
        z2_bounds = (0, 50)

        # Menyelesaikan permasalahan dengan metode simplex
        result = linprog(c, A_ub=A, b_ub=b, bounds=[x2_bounds, y2_bounds, z2_bounds])
        berat_kacang_3    = round(result.x[0],3)
        berat_buah_3      = round(result.x[1],3)
        berat_skim_susu_3 = round(result.x[2],3)

        #makan pagi menu 2
        A = [[karbohidrat_3['karbohidrat']/100, protein_3['karbohidrat']/100, lemak_3['karbohidrat']/100],
            [karbohidrat_3['protein']/100, protein_3['protein']/100, lemak_3['protein']/100],
            [karbohidrat_3['lemak']/100, protein_3['lemak']/100, lemak_3['lemak']/100]]
        b1 = [karbo_pagi - sayuran_a_3['karbohidrat'] - sayuran_b_3['karbohidrat']/4, protein_pagi - sayuran_a_3['protein'] - sayuran_b_3['protein']/4, lemak_pagi - sayuran_a_3['lemak'] - sayuran_b_3['lemak']/4]
        b2 = [karbo_siang - sayuran_a_3['karbohidrat'] - sayuran_b_3['karbohidrat']/2, protein_siang - sayuran_a_3['protein'] - sayuran_b_3['protein']/2, lemak_siang - sayuran_a_3['lemak'] - sayuran_b_3['lemak']/2]
        c = [-1, -1, -1]

        # Menentukan batasan-batasan variabel
        x3_bounds = (1, karbo_siang*2)
        if kalori_harian_final < 1500:
          y3_bounds = (15, None)
        else:
          y3_bounds = (20, None)
        z3_bounds = (0, None)

        # Menyelesaikan permasalahan dengan metode simplex
        max_iterasi = 100 

        for _ in range(max_iterasi):
            result = linprog(c, A_ub=A, b_ub=b1, bounds=[x3_bounds, y3_bounds, z3_bounds])
            if result is not None:
                break

        berat_karbo_pagi_3   = round(result.x[0],3)
        berat_protein_pagi_3 = round(result.x[1],3)
        berat_lemak_pagi_3   = round(result.x[2],3)

        #makan siang malam menu 3
        result2 = linprog(c, A_ub=A, b_ub=b2, bounds=[x3_bounds, y3_bounds, z3_bounds])
        berat_karbo_siang_3   = round(result2.x[0],3)
        berat_protein_siang_3 = round(result2.x[1],3)
        berat_lemak_siang_3   = round(result2.x[2],3)

        total_karbohidrat_3 = round((karbohidrat_3['karbohidrat'] / 100) * (2 * berat_karbo_siang_3 + berat_karbo_pagi_3) + (protein_3['karbohidrat'] / 100) * (2 * berat_protein_siang_3 + berat_protein_pagi_3) + (lemak_3['karbohidrat'] / 100) * (2 * berat_lemak_siang_3 + berat_lemak_pagi_3) 
        + (3 * sayuran_a_3['karbohidrat']) + (1.25 * sayuran_b_3['karbohidrat'])
        + (buah_3['karbohidrat'] / 100) * (3 * berat_buah_3) + (kacang_3['karbohidrat'] / 100) * (3 * berat_kacang_3) + (skim_susu_3['karbohidrat'] / 100) * (3 * berat_skim_susu_3), 3)

        total_protein_3 = round((karbohidrat_3['protein'] / 100) * (2 * berat_karbo_siang_3 + berat_karbo_pagi_3) + (protein_3['protein'] / 100) * (2 * berat_protein_siang_3 + berat_protein_pagi_3) + (lemak_3['protein'] / 100) * (2 * berat_lemak_siang_3 + berat_lemak_pagi_3) 
        + (3 * sayuran_a_3['protein']) + (1.25 * sayuran_b_3['protein'])
        + (buah_3['protein'] / 100) * (3 * berat_buah_3) + (kacang_3['protein'] / 100) * (3 * berat_kacang_3) + (skim_susu_3['protein'] / 100) * (3 * berat_skim_susu_3), 3)

        total_lemak_3 = round((karbohidrat_3['lemak'] / 100) * (2 * berat_karbo_siang_3 + berat_karbo_pagi_3) + (protein_3['lemak'] / 100) * (2 * berat_protein_siang_3 + berat_protein_pagi_3) + (lemak_3['lemak'] / 100) * (2 * berat_lemak_siang_3 + berat_lemak_pagi_3) 
        + (3 * sayuran_a_3['lemak']) + (1.25 * sayuran_b_3['lemak'])
        + (buah_3['lemak'] / 100) * (3 * berat_buah_3) + (kacang_3['lemak'] / 100) * (3 * berat_kacang_3) + (skim_susu_3['lemak'] / 100) * (3 * berat_skim_susu_3), 3)

        total_kalori_3 = round (total_karbohidrat_3 * 4 + total_protein_3 * 4 + total_lemak_3 * 9 , 3)

      protein_exclude.append(protein_3['id'])
      lemak_exclude.append(lemak_3['id'])
      sayuran_a_exclude.append(sayuran_a_3['id'])
      sayuran_b_exclude.append(sayuran_b_3['id'])
      kacang_exclude.append(kacang_3['id'])
      buah_exclude.append(buah_3['id'])

      #Menu 4
      total_kalori_4 = 0

      while total_kalori_4 < kalori_harian_final * 0.9:

        karbohidrat_index = random.randint(0, data_karbohidrat.shape[0] - 1)
        karbohidrat_4     = data_karbohidrat.iloc[karbohidrat_index]

        filtered_data_protein = data_protein[~data_protein['id'].isin(protein_exclude)]
        protein_index   = random.randint(0, filtered_data_protein.shape[0] - 1)
        protein_4       = filtered_data_protein.iloc[protein_index]

        filtered_data_lemak = data_lemak[~data_lemak['id'].isin(lemak_exclude)]
        lemak_index     = random.randint(0, filtered_data_lemak.shape[0] - 1)
        lemak_4         = filtered_data_lemak.iloc[lemak_index]

        filtered_data_sayuran_a = data_sayuran_a[~data_sayuran_a['id'].isin(sayuran_a_exclude)]
        sayuran_a_index = random.randint(0, filtered_data_sayuran_a.shape[0] - 1)
        sayuran_a_4     = filtered_data_sayuran_a.iloc[sayuran_a_index]

        filtered_data_sayuran_b = data_sayuran_b[~data_sayuran_b['id'].isin(sayuran_b_exclude)]
        sayuran_b_index = random.randint(0, filtered_data_sayuran_b.shape[0] - 1)
        sayuran_b_4     = filtered_data_sayuran_b.iloc[sayuran_b_index]

        filtered_data_kacang = data_kacang[~data_kacang['id'].isin(kacang_exclude)]
        kacang_index    = random.randint(0, filtered_data_kacang.shape[0] - 1)
        kacang_4        = filtered_data_kacang.iloc[kacang_index]
        
        filtered_data_buah = data_buah[~data_buah['id'].isin(buah_exclude)]
        buah_index      = random.randint(0, filtered_data_buah.shape[0] - 1)
        buah_4          = filtered_data_buah.iloc[buah_index]

        skim_susu_index = random.randint(0, data_skim_susu.shape[0] - 1)
        skim_susu_4     = data_skim_susu.iloc[skim_susu_index]

        #camilan menu 2
        #koefisien matriks
        A = [[kacang_4['karbohidrat']/100, buah_4['karbohidrat']/100, skim_susu_4['karbohidrat']/100],
            [kacang_4['protein']/100, buah_4['protein']/100, skim_susu_4['protein']/100],
            [kacang_4['lemak']/100, buah_4['lemak']/100, skim_susu_4['lemak']/100]]
        b = [karbo_camilan, protein_camilan, lemak_camilan]
        c = [-1, -1, -1]

        # Menentukan batasan-batasan variabel
        x2_bounds = (1, None)
        y2_bounds = (1, 125)
        z2_bounds = (0, 50)

        # Menyelesaikan permasalahan dengan metode simplex
        result = linprog(c, A_ub=A, b_ub=b, bounds=[x2_bounds, y2_bounds, z2_bounds])
        berat_kacang_4    = round(result.x[0],3)
        berat_buah_4      = round(result.x[1],3)
        berat_skim_susu_4 = round(result.x[2],3)

        #makan pagi menu 2
        A = [[karbohidrat_4['karbohidrat']/100, protein_4['karbohidrat']/100, lemak_4['karbohidrat']/100],
            [karbohidrat_4['protein']/100, protein_4['protein']/100, lemak_4['protein']/100],
            [karbohidrat_4['lemak']/100, protein_4['lemak']/100, lemak_4['lemak']/100]]
        b1 = [karbo_pagi - sayuran_a_4['karbohidrat'] - sayuran_b_4['karbohidrat']/4, protein_pagi - sayuran_a_4['protein'] - sayuran_b_4['protein']/4, lemak_pagi - sayuran_a_4['lemak'] - sayuran_b_4['lemak']/4]
        b2 = [karbo_siang - sayuran_a_4['karbohidrat'] - sayuran_b_4['karbohidrat']/2, protein_siang - sayuran_a_4['protein'] - sayuran_b_4['protein']/2, lemak_siang - sayuran_a_4['lemak'] - sayuran_b_4['lemak']/2]
        c = [-1, -1, -1]

        # Menentukan batasan-batasan variabel
        x3_bounds = (1, karbo_siang*2)
        if kalori_harian_final < 1500:
          y3_bounds = (15, None)
        else:
          y3_bounds = (20, None)
        z3_bounds = (0, None)

        # Menyelesaikan permasalahan dengan metode simplex
        max_iterasi = 100 

        for _ in range(max_iterasi):
            result = linprog(c, A_ub=A, b_ub=b1, bounds=[x3_bounds, y3_bounds, z3_bounds])
            if result is not None:
                break

        berat_karbo_pagi_4   = round(result.x[0],3)
        berat_protein_pagi_4 = round(result.x[1],3)
        berat_lemak_pagi_4   = round(result.x[2],3)

        #makan siang malam menu 1
        result2 = linprog(c, A_ub=A, b_ub=b2, bounds=[x3_bounds, y3_bounds, z3_bounds])
        berat_karbo_siang_4   = round(result2.x[0],3)
        berat_protein_siang_4 = round(result2.x[1],3)
        berat_lemak_siang_4   = round(result2.x[2],3)

        total_karbohidrat_4 = round((karbohidrat_4['karbohidrat'] / 100) * (2 * berat_karbo_siang_4 + berat_karbo_pagi_4) + (protein_4['karbohidrat'] / 100) * (2 * berat_protein_siang_4 + berat_protein_pagi_4) + (lemak_4['karbohidrat'] / 100) * (2 * berat_lemak_siang_4 + berat_lemak_pagi_4) 
        + (3 * sayuran_a_4['karbohidrat']) + (1.25 * sayuran_b_4['karbohidrat'])
        + (buah_4['karbohidrat'] / 100) * (3 * berat_buah_4) + (kacang_4['karbohidrat'] / 100) * (3 * berat_kacang_4) + (skim_susu_4['karbohidrat'] / 100) * (3 * berat_skim_susu_4), 3)

        total_protein_4 = round((karbohidrat_4['protein'] / 100) * (2 * berat_karbo_siang_4 + berat_karbo_pagi_4) + (protein_4['protein'] / 100) * (2 * berat_protein_siang_4 + berat_protein_pagi_4) + (lemak_4['protein'] / 100) * (2 * berat_lemak_siang_4 + berat_lemak_pagi_4) 
        + (3 * sayuran_a_4['protein']) + (1.25 * sayuran_b_4['protein'])
        + (buah_4['protein'] / 100) * (3 * berat_buah_4) + (kacang_4['protein'] / 100) * (3 * berat_kacang_4) + (skim_susu_4['protein'] / 100) * (3 * berat_skim_susu_4), 3)

        total_lemak_4 = round((karbohidrat_4['lemak'] / 100) * (2 * berat_karbo_siang_4 + berat_karbo_pagi_4) + (protein_4['lemak'] / 100) * (2 * berat_protein_siang_4 + berat_protein_pagi_4) + (lemak_4['lemak'] / 100) * (2 * berat_lemak_siang_4 + berat_lemak_pagi_4) 
        + (3 * sayuran_a_4['lemak']) + (1.25 * sayuran_b_4['lemak'])
        + (buah_4['lemak'] / 100) * (3 * berat_buah_4) + (kacang_4['lemak'] / 100) * (3 * berat_kacang_4) + (skim_susu_4['lemak'] / 100) * (3 * berat_skim_susu_4), 3)

        total_kalori_4 = round (total_karbohidrat_4 * 4 + total_protein_4 * 4 + total_lemak_4 * 9 , 3)
      

      protein_exclude.append(protein_4['id'])
      lemak_exclude.append(lemak_4['id'])
      sayuran_a_exclude.append(sayuran_a_4['id'])
      sayuran_b_exclude.append(sayuran_b_4['id'])
      kacang_exclude.append(kacang_4['id'])
      buah_exclude.append(buah_4['id'])

      #Menu 5

      total_kalori_5 = 0

      while total_kalori_5 < kalori_harian_final * 0.9:
        karbohidrat_index = random.randint(0, data_karbohidrat.shape[0] - 1)
        karbohidrat_5     = data_karbohidrat.iloc[karbohidrat_index]

        filtered_data_protein = data_protein[~data_protein['id'].isin(protein_exclude)]
        protein_index   = random.randint(0, filtered_data_protein.shape[0] - 1)
        protein_5       = filtered_data_protein.iloc[protein_index]

        filtered_data_lemak = data_lemak[~data_lemak['id'].isin(lemak_exclude)]
        lemak_index     = random.randint(0, filtered_data_lemak.shape[0] - 1)
        lemak_5         = filtered_data_lemak.iloc[lemak_index]

        filtered_data_sayuran_a = data_sayuran_a[~data_sayuran_a['id'].isin(sayuran_a_exclude)]
        sayuran_a_index = random.randint(0, filtered_data_sayuran_a.shape[0] - 1)
        sayuran_a_5     = filtered_data_sayuran_a.iloc[sayuran_a_index]

        filtered_data_sayuran_b = data_sayuran_b[~data_sayuran_b['id'].isin(sayuran_b_exclude)]
        sayuran_b_index = random.randint(0, filtered_data_sayuran_b.shape[0] - 1)
        sayuran_b_5     = filtered_data_sayuran_b.iloc[sayuran_b_index]

        filtered_data_kacang = data_kacang[~data_kacang['id'].isin(kacang_exclude)]
        kacang_index    = random.randint(0, filtered_data_kacang.shape[0] - 1)
        kacang_5        = filtered_data_kacang.iloc[kacang_index]
        
        filtered_data_buah = data_buah[~data_buah['id'].isin(buah_exclude)]
        buah_index      = random.randint(0, filtered_data_buah.shape[0] - 1)
        buah_5          = filtered_data_buah.iloc[buah_index]

        skim_susu_index = random.randint(0, data_skim_susu.shape[0] - 1)
        skim_susu_5     = data_skim_susu.iloc[skim_susu_index]

        #camilan menu 2
        #koefisien matriks
        A = [[kacang_5['karbohidrat']/100, buah_5['karbohidrat']/100, skim_susu_5['karbohidrat']/100],
            [kacang_5['protein']/100, buah_5['protein']/100, skim_susu_5['protein']/100],
            [kacang_5['lemak']/100, buah_5['lemak']/100, skim_susu_5['lemak']/100]]
        b = [karbo_camilan, protein_camilan, lemak_camilan]
        c = [-1, -1, -1]

        # Menentukan batasan-batasan variabel
        x2_bounds = (1, None)
        y2_bounds = (1, 125)
        z2_bounds = (0, 50)

        # Menyelesaikan permasalahan dengan metode simplex
        result = linprog(c, A_ub=A, b_ub=b, bounds=[x2_bounds, y2_bounds, z2_bounds])
        berat_kacang_5    = round(result.x[0],3)
        berat_buah_5      = round(result.x[1],3)
        berat_skim_susu_5 = round(result.x[2],3)

        #makan pagi menu 2
        A = [[karbohidrat_5['karbohidrat']/100, protein_5['karbohidrat']/100, lemak_5['karbohidrat']/100],
            [karbohidrat_5['protein']/100, protein_5['protein']/100, lemak_5['protein']/100],
            [karbohidrat_5['lemak']/100, protein_5['lemak']/100, lemak_5['lemak']/100]]
        b1 = [karbo_pagi - sayuran_a_5['karbohidrat'] - sayuran_b_5['karbohidrat']/4, protein_pagi - sayuran_a_5['protein'] - sayuran_b_5['protein']/4, lemak_pagi - sayuran_a_5['lemak'] - sayuran_b_5['lemak']/4]
        b2 = [karbo_siang - sayuran_a_5['karbohidrat'] - sayuran_b_5['karbohidrat']/2, protein_siang - sayuran_a_5['protein'] - sayuran_b_5['protein']/2, lemak_siang - sayuran_a_5['lemak'] - sayuran_b_5['lemak']/2]
        c = [-1, -1, -1]

        # Menentukan batasan-batasan variabel
        x3_bounds = (1, karbo_siang*2)
        if kalori_harian_final < 1500:
          y3_bounds = (15, None)
        else:
          y3_bounds = (20, None)
        z3_bounds = (0, None)

        # Menyelesaikan permasalahan dengan metode simplex
        max_iterasi = 100 

        for _ in range(max_iterasi):
            result = linprog(c, A_ub=A, b_ub=b1, bounds=[x3_bounds, y3_bounds, z3_bounds])
            if result is not None:
                break

        berat_karbo_pagi_5   = round(result.x[0],3)
        berat_protein_pagi_5 = round(result.x[1],3)
        berat_lemak_pagi_5   = round(result.x[2],3)

        #makan siang malam menu 1
        result2 = linprog(c, A_ub=A, b_ub=b2, bounds=[x3_bounds, y3_bounds, z3_bounds])
        berat_karbo_siang_5   = round(result2.x[0],3)
        berat_protein_siang_5 = round(result2.x[1],3)
        berat_lemak_siang_5   = round(result2.x[2],3)

        total_karbohidrat_5 = round((karbohidrat_5['karbohidrat'] / 100) * (2 * berat_karbo_siang_5 + berat_karbo_pagi_5) + (protein_5['karbohidrat'] / 100) * (2 * berat_protein_siang_5 + berat_protein_pagi_5) + (lemak_5['karbohidrat'] / 100) * (2 * berat_lemak_siang_5 + berat_lemak_pagi_5) 
        + (3 * sayuran_a_5['karbohidrat']) + (1.25 * sayuran_b_5['karbohidrat'])
        + (buah_5['karbohidrat'] / 100) * (3 * berat_buah_5) + (kacang_5['karbohidrat'] / 100) * (3 * berat_kacang_5) + (skim_susu_5['karbohidrat'] / 100) * (3 * berat_skim_susu_5), 3)

        total_protein_5 = round((karbohidrat_5['protein'] / 100) * (2 * berat_karbo_siang_5 + berat_karbo_pagi_5) + (protein_5['protein'] / 100) * (2 * berat_protein_siang_5 + berat_protein_pagi_5) + (lemak_5['protein'] / 100) * (2 * berat_lemak_siang_5 + berat_lemak_pagi_5) 
        + (3 * sayuran_a_5['protein']) + (1.25 * sayuran_b_5['protein'])
        + (buah_5['protein'] / 100) * (3 * berat_buah_5) + (kacang_5['protein'] / 100) * (3 * berat_kacang_5) + (skim_susu_5['protein'] / 100) * (3 * berat_skim_susu_5), 3)

        total_lemak_5 = round((karbohidrat_5['lemak'] / 100) * (2 * berat_karbo_siang_5 + berat_karbo_pagi_5) + (protein_5['lemak'] / 100) * (2 * berat_protein_siang_5 + berat_protein_pagi_5) + (lemak_5['lemak'] / 100) * (2 * berat_lemak_siang_5 + berat_lemak_pagi_5) 
        + (3 * sayuran_a_5['lemak']) + (1.25 * sayuran_b_5['lemak'])
        + (buah_5['lemak'] / 100) * (3 * berat_buah_5) + (kacang_5['lemak'] / 100) * (3 * berat_kacang_5) + (skim_susu_5['lemak'] / 100) * (3 * berat_skim_susu_5), 3)

        total_kalori_5 = round (total_karbohidrat_5 * 4 + total_protein_5 * 4 + total_lemak_5 * 9 , 3)
        
      menu_1 = {
        'berat_buah'       : berat_buah_1,
        'berat_kacang'     : berat_kacang_1,
        'berat_skim_susu'  : berat_skim_susu_1,
        'berat_karbo_pagi' : berat_karbo_pagi_1,
        'berat_karbo_siang': berat_karbo_siang_1,
        'berat_protein_pagi'  : berat_protein_pagi_1,
        'berat_protein_siang' : berat_protein_siang_1,
        'berat_lemak_pagi'    : berat_lemak_pagi_1,
        'berat_lemak_siang'   : berat_lemak_siang_1,
        'kacang'    : kacang_1['nama'],
        'buah'      : buah_1['nama'],
        'skim_susu' : skim_susu_1['nama'],
        'sayuran_a' : sayuran_a_1['nama'],
        'sayuran_b' : sayuran_b_1['nama'],
        'karbohidrat': karbohidrat_1['nama'],
        'protein'   : protein_1['nama'],
        'lemak'     : lemak_1['nama'],
        'total_karbo'     : total_karbohidrat_1,
        'total_protein'   : total_protein_1,
        'total_lemak'     : total_lemak_1,
        'total_kalori'    : total_kalori_1,
      }
      menu_2 = {
        'berat_buah'       : berat_buah_2,
        'berat_kacang'     : berat_kacang_2,
        'berat_skim_susu'  : berat_skim_susu_2,
        'berat_karbo_pagi' : berat_karbo_pagi_2,
        'berat_karbo_siang': berat_karbo_siang_2,
        'berat_protein_pagi'  : berat_protein_pagi_2,
        'berat_protein_siang' : berat_protein_siang_2,
        'berat_lemak_pagi'    : berat_lemak_pagi_2,
        'berat_lemak_siang'   : berat_lemak_siang_2,
        'kacang'    : kacang_2['nama'],
        'buah'      : buah_2['nama'],
        'skim_susu' : skim_susu_2['nama'],
        'sayuran_a' : sayuran_a_2['nama'],
        'sayuran_b' : sayuran_b_2['nama'],
        'karbohidrat': karbohidrat_2['nama'],
        'protein'   : protein_2['nama'],
        'lemak'     : lemak_2['nama'],
        'total_karbo'     : total_karbohidrat_2,
        'total_protein'   : total_protein_2,
        'total_lemak'     : total_lemak_2,
        'total_kalori'    : total_kalori_2,
      }
      menu_3 = {
        'berat_buah'       : berat_buah_3,
        'berat_kacang'     : berat_kacang_3,
        'berat_skim_susu'  : berat_skim_susu_3,
        'berat_karbo_pagi' : berat_karbo_pagi_3,
        'berat_karbo_siang': berat_karbo_siang_3,
        'berat_protein_pagi'  : berat_protein_pagi_3,
        'berat_protein_siang' : berat_protein_siang_3,
        'berat_lemak_pagi'    : berat_lemak_pagi_3,
        'berat_lemak_siang'   : berat_lemak_siang_3,
        'kacang'    : kacang_3['nama'],
        'buah'      : buah_3['nama'],
        'skim_susu' : skim_susu_3['nama'],
        'sayuran_a' : sayuran_a_3['nama'],
        'sayuran_b' : sayuran_b_3['nama'],
        'karbohidrat': karbohidrat_3['nama'],
        'protein'   : protein_3['nama'],
        'lemak'     : lemak_3['nama'],
        'total_karbo'     : total_karbohidrat_3,
        'total_protein'   : total_protein_3,
        'total_lemak'     : total_lemak_3,
        'total_kalori'    : total_kalori_3,
      }

      menu_4 = {
        'berat_buah'       : berat_buah_4,
        'berat_kacang'     : berat_kacang_4,
        'berat_skim_susu'  : berat_skim_susu_4,
        'berat_karbo_pagi' : berat_karbo_pagi_4,
        'berat_karbo_siang': berat_karbo_siang_4,
        'berat_protein_pagi'  : berat_protein_pagi_4,
        'berat_protein_siang' : berat_protein_siang_4,
        'berat_lemak_pagi'    : berat_lemak_pagi_4,
        'berat_lemak_siang'   : berat_lemak_siang_4,
        'kacang'    : kacang_4['nama'],
        'buah'      : buah_4['nama'],
        'skim_susu' : skim_susu_4['nama'],
        'sayuran_a' : sayuran_a_4['nama'],
        'sayuran_b' : sayuran_b_4['nama'],
        'karbohidrat': karbohidrat_4['nama'],
        'protein'   : protein_4['nama'],
        'lemak'     : lemak_4['nama'],
        'total_karbo'     : total_karbohidrat_4,
        'total_protein'   : total_protein_4,
        'total_lemak'     : total_lemak_4,
        'total_kalori'    : total_kalori_4,
      }

      menu_5 = {
        'berat_buah'       : berat_buah_5,
        'berat_kacang'     : berat_kacang_5,
        'berat_skim_susu'  : berat_skim_susu_5,
        'berat_karbo_pagi' : berat_karbo_pagi_5,
        'berat_karbo_siang': berat_karbo_siang_5,
        'berat_protein_pagi'  : berat_protein_pagi_5,
        'berat_protein_siang' : berat_protein_siang_5,
        'berat_lemak_pagi'    : berat_lemak_pagi_5,
        'berat_lemak_siang'   : berat_lemak_siang_5,
        'kacang'    : kacang_5['nama'],
        'buah'      : buah_5['nama'],
        'skim_susu' : skim_susu_5['nama'],
        'sayuran_a' : sayuran_a_5['nama'],
        'sayuran_b' : sayuran_b_5['nama'],
        'karbohidrat': karbohidrat_5['nama'],
        'protein'   : protein_5['nama'],
        'lemak'     : lemak_5['nama'],
        'total_karbo'     : total_karbohidrat_5,
        'total_protein'   : total_protein_5,
        'total_lemak'     : total_lemak_5,
        'total_kalori'    : total_kalori_5,
      }

      return render(request, 'menupage.html', {'data_personal': data_personal, 'data_gizi_harian' : data_gizi_harian, 'jenis_diet' : jenis_diet, 'menu_1' : menu_1, 'menu_2' : menu_2, 'menu_3' : menu_3, 'menu_4' : menu_4, 'menu_5' : menu_5})
    
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

    berat_buah_1          = request.POST.get('berat_buah_1')
    berat_kacang_1        = request.POST.get('berat_kacang_1')
    berat_skim_susu_1     = request.POST.get('berat_skim_susu_1')
    berat_karbo_pagi_1    = request.POST.get('berat_karbo_pagi_1')
    berat_karbo_siang_1   = request.POST.get('berat_karbo_siang_1')
    berat_protein_pagi_1  = request.POST.get('berat_protein_pagi_1')
    berat_protein_siang_1 = request.POST.get('berat_protein_siang_1')
    berat_lemak_pagi_1    = request.POST.get('berat_lemak_pagi_1')
    berat_lemak_siang_1   = request.POST.get('berat_lemak_siang_1')
    kacang_1              = request.POST.get('kacang_1')
    buah_1                = request.POST.get('buah_1')
    skim_susu_1           = request.POST.get('skim_susu_1')
    sayuran_a_1           = request.POST.get('sayuran_a_1')
    sayuran_b_1           = request.POST.get('sayuran_b_1')
    karbohidrat_1         = request.POST.get('karbohidrat_1')
    protein_1             = request.POST.get('protein_1')
    lemak_1               = request.POST.get('lemak_1')
    total_karbohidrat_1   = request.POST.get('total_karbohidrat_1')
    total_protein_1       = request.POST.get('total_protein_1')
    total_lemak_1         = request.POST.get('total_lemak_1')
    total_kalori_1        = request.POST.get('total_kalori_1')

    berat_buah_2          = request.POST.get('berat_buah_2')
    berat_kacang_2        = request.POST.get('berat_kacang_2')
    berat_skim_susu_2     = request.POST.get('berat_skim_susu_2')
    berat_karbo_pagi_2    = request.POST.get('berat_karbo_pagi_2')
    berat_karbo_siang_2   = request.POST.get('berat_karbo_siang_2')
    berat_protein_pagi_2  = request.POST.get('berat_protein_pagi_2')
    berat_protein_siang_2 = request.POST.get('berat_protein_siang_2')
    berat_lemak_pagi_2    = request.POST.get('berat_lemak_pagi_2')
    berat_lemak_siang_2   = request.POST.get('berat_lemak_siang_2')
    kacang_2              = request.POST.get('kacang_2')
    buah_2                = request.POST.get('buah_2')
    skim_susu_2           = request.POST.get('skim_susu_2')
    sayuran_a_2           = request.POST.get('sayuran_a_2')
    sayuran_b_2           = request.POST.get('sayuran_b_2')
    karbohidrat_2         = request.POST.get('karbohidrat_2')
    protein_2             = request.POST.get('protein_2')
    lemak_2               = request.POST.get('lemak_2')
    total_karbohidrat_2   = request.POST.get('total_karbohidrat_2')
    total_protein_2       = request.POST.get('total_protein_2')
    total_lemak_2         = request.POST.get('total_lemak_2')
    total_kalori_2        = request.POST.get('total_kalori_2')

    berat_buah_3          = request.POST.get('berat_buah_3')
    berat_kacang_3        = request.POST.get('berat_kacang_3')
    berat_skim_susu_3     = request.POST.get('berat_skim_susu_3')
    berat_karbo_pagi_3    = request.POST.get('berat_karbo_pagi_3')
    berat_karbo_siang_3   = request.POST.get('berat_karbo_siang_3')
    berat_protein_pagi_3  = request.POST.get('berat_protein_pagi_3')
    berat_protein_siang_3 = request.POST.get('berat_protein_siang_3')
    berat_lemak_pagi_3    = request.POST.get('berat_lemak_pagi_3')
    berat_lemak_siang_3   = request.POST.get('berat_lemak_siang_3')
    kacang_3              = request.POST.get('kacang_3')
    buah_3                = request.POST.get('buah_3')
    skim_susu_3           = request.POST.get('skim_susu_3')
    sayuran_a_3           = request.POST.get('sayuran_a_3')
    sayuran_b_3           = request.POST.get('sayuran_b_3')
    karbohidrat_3         = request.POST.get('karbohidrat_3')
    protein_3             = request.POST.get('protein_3')
    lemak_3               = request.POST.get('lemak_3')
    total_karbohidrat_3   = request.POST.get('total_karbohidrat_3')
    total_protein_3       = request.POST.get('total_protein_3')
    total_lemak_3         = request.POST.get('total_lemak_3')
    total_kalori_3        = request.POST.get('total_kalori_3')

    berat_buah_4          = request.POST.get('berat_buah_4')
    berat_kacang_4        = request.POST.get('berat_kacang_4')
    berat_skim_susu_4     = request.POST.get('berat_skim_susu_4')
    berat_karbo_pagi_4    = request.POST.get('berat_karbo_pagi_4')
    berat_karbo_siang_4   = request.POST.get('berat_karbo_siang_4')
    berat_protein_pagi_4  = request.POST.get('berat_protein_pagi_4')
    berat_protein_siang_4 = request.POST.get('berat_protein_siang_4')
    berat_lemak_pagi_4    = request.POST.get('berat_lemak_pagi_4')
    berat_lemak_siang_4   = request.POST.get('berat_lemak_siang_4')
    kacang_4              = request.POST.get('kacang_4')
    buah_4                = request.POST.get('buah_4')
    skim_susu_4           = request.POST.get('skim_susu_4')
    sayuran_a_4           = request.POST.get('sayuran_a_4')
    sayuran_b_4           = request.POST.get('sayuran_b_4')
    karbohidrat_4         = request.POST.get('karbohidrat_4')
    protein_4             = request.POST.get('protein_4')
    lemak_4               = request.POST.get('lemak_4')
    total_karbohidrat_4   = request.POST.get('total_karbohidrat_4')
    total_protein_4       = request.POST.get('total_protein_4')
    total_lemak_4         = request.POST.get('total_lemak_4')
    total_kalori_4        = request.POST.get('total_kalori_4')

    berat_buah_5          = request.POST.get('berat_buah_5')
    berat_kacang_5        = request.POST.get('berat_kacang_5')
    berat_skim_susu_5     = request.POST.get('berat_skim_susu_5')
    berat_karbo_pagi_5    = request.POST.get('berat_karbo_pagi_5')
    berat_karbo_siang_5   = request.POST.get('berat_karbo_siang_5')
    berat_protein_pagi_5  = request.POST.get('berat_protein_pagi_5')
    berat_protein_siang_5 = request.POST.get('berat_protein_siang_5')
    berat_lemak_pagi_5    = request.POST.get('berat_lemak_pagi_5')
    berat_lemak_siang_5   = request.POST.get('berat_lemak_siang_5')
    kacang_5              = request.POST.get('kacang_5')
    buah_5                = request.POST.get('buah_5')
    skim_susu_5           = request.POST.get('skim_susu_5')
    sayuran_a_5           = request.POST.get('sayuran_a_5')
    sayuran_b_5           = request.POST.get('sayuran_b_5')
    karbohidrat_5         = request.POST.get('karbohidrat_5')
    protein_5             = request.POST.get('protein_5')
    lemak_5               = request.POST.get('lemak_5')
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
      'berat_buah'       : berat_buah_1,
      'berat_kacang'     : berat_kacang_1,
      'berat_skim_susu'  : berat_skim_susu_1,
      'berat_karbo_pagi' : berat_karbo_pagi_1,
      'berat_karbo_siang': berat_karbo_siang_1,
      'berat_protein_pagi'  : berat_protein_pagi_1,
      'berat_protein_siang' : berat_protein_siang_1,
      'berat_lemak_pagi'    : berat_lemak_pagi_1,
      'berat_lemak_siang'   : berat_lemak_siang_1,
      'kacang'    : kacang_1,
      'buah'      : buah_1,
      'skim_susu' : skim_susu_1,
      'sayuran_a' : sayuran_a_1,
      'sayuran_b' : sayuran_b_1,
      'karbohidrat': karbohidrat_1,
      'protein'   : protein_1,
      'lemak'     : lemak_1,
      'total_karbo'     : total_karbohidrat_1,
      'total_protein'   : total_protein_1,
      'total_lemak'     : total_lemak_1,
      'total_kalori'    : total_kalori_1,
    }
    menu_2 = {
      'berat_buah'       : berat_buah_2,
      'berat_kacang'     : berat_kacang_2,
      'berat_skim_susu'  : berat_skim_susu_2,
      'berat_karbo_pagi' : berat_karbo_pagi_2,
      'berat_karbo_siang': berat_karbo_siang_2,
      'berat_protein_pagi'  : berat_protein_pagi_2,
      'berat_protein_siang' : berat_protein_siang_2,
      'berat_lemak_pagi'    : berat_lemak_pagi_2,
      'berat_lemak_siang'   : berat_lemak_siang_2,
      'kacang'    : kacang_2,
      'buah'      : buah_2,
      'skim_susu' : skim_susu_2,
      'sayuran_a' : sayuran_a_2,
      'sayuran_b' : sayuran_b_2,
      'karbohidrat': karbohidrat_2,
      'protein'   : protein_2,
      'lemak'     : lemak_2,
      'total_karbo'     : total_karbohidrat_2,
      'total_protein'   : total_protein_2,
      'total_lemak'     : total_lemak_2,
      'total_kalori'    : total_kalori_2,
    }
    menu_3 = {
      'berat_buah'       : berat_buah_3,
      'berat_kacang'     : berat_kacang_3,
      'berat_skim_susu'  : berat_skim_susu_3,
      'berat_karbo_pagi' : berat_karbo_pagi_3,
      'berat_karbo_siang': berat_karbo_siang_3,
      'berat_protein_pagi'  : berat_protein_pagi_3,
      'berat_protein_siang' : berat_protein_siang_3,
      'berat_lemak_pagi'    : berat_lemak_pagi_3,
      'berat_lemak_siang'   : berat_lemak_siang_3,
      'kacang'    : kacang_3,
      'buah'      : buah_3,
      'skim_susu' : skim_susu_3,
      'sayuran_a' : sayuran_a_3,
      'sayuran_b' : sayuran_b_3,
      'karbohidrat': karbohidrat_3,
      'protein'   : protein_3,
      'lemak'     : lemak_3,
      'total_karbo'     : total_karbohidrat_3,
      'total_protein'   : total_protein_3,
      'total_lemak'     : total_lemak_3,
      'total_kalori'    : total_kalori_3,
    }

    menu_4 = {
      'berat_buah'       : berat_buah_4,
      'berat_kacang'     : berat_kacang_4,
      'berat_skim_susu'  : berat_skim_susu_4,
      'berat_karbo_pagi' : berat_karbo_pagi_4,
      'berat_karbo_siang': berat_karbo_siang_4,
      'berat_protein_pagi'  : berat_protein_pagi_4,
      'berat_protein_siang' : berat_protein_siang_4,
      'berat_lemak_pagi'    : berat_lemak_pagi_4,
      'berat_lemak_siang'   : berat_lemak_siang_4,
      'kacang'    : kacang_4,
      'buah'      : buah_4,
      'skim_susu' : skim_susu_4,
      'sayuran_a' : sayuran_a_4,
      'sayuran_b' : sayuran_b_4,
      'karbohidrat': karbohidrat_4,
      'protein'   : protein_4,
      'lemak'     : lemak_4,
      'total_karbo'     : total_karbohidrat_4,
      'total_protein'   : total_protein_4,
      'total_lemak'     : total_lemak_4,
      'total_kalori'    : total_kalori_4,
    }

    menu_5 = {
      'berat_buah'       : berat_buah_5,
      'berat_kacang'     : berat_kacang_5,
      'berat_skim_susu'  : berat_skim_susu_5,
      'berat_karbo_pagi' : berat_karbo_pagi_5,
      'berat_karbo_siang': berat_karbo_siang_5,
      'berat_protein_pagi'  : berat_protein_pagi_5,
      'berat_protein_siang' : berat_protein_siang_5,
      'berat_lemak_pagi'    : berat_lemak_pagi_5,
      'berat_lemak_siang'   : berat_lemak_siang_5,
      'kacang'    : kacang_5,
      'buah'      : buah_5,
      'skim_susu' : skim_susu_5,
      'sayuran_a' : sayuran_a_5,
      'sayuran_b' : sayuran_b_5,
      'karbohidrat': karbohidrat_5,
      'protein'   : protein_5,
      'lemak'     : lemak_5,
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

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="output.pdf"'

    # Buat dokumen PDF dari HTML
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    # Jika berhasil membuat PDF, kembalikan response
    if pisa_status.err:
        return HttpResponse('Gagal membuat PDF: %s' % pisa_status.err)
    return response
    
  return render(request, 'inputpage.html')