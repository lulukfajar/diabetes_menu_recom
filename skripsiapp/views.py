from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect
from django.template import RequestContext

def landingpage(request):
  template = loader.get_template('landingpage.html')
  return HttpResponse(template.render())

def inputpage(request):
 return render(request, 'inputpage.html')

def menupage(request):
  template = loader.get_template('menupage.html')
  return HttpResponse(template.render())

def prosesdata(request):
  data_personal       = {}
  jenis_kelamin_2     =''
  tingkat_aktivitas_2 =''
  penyakit_penyerta_2 =''
  data_gizi_harian    = {}

  if request.method == 'POST':
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

    if jenis_kelamin == 'p':
      jenis_kelamin_2 = 'perempuan'
    else:
      jenis_kelamin_2 = 'laki-laki'

    if tingkat_aktivitas == '1' :
      tingkat_aktivitas_2 = 'Sangat Ringan'
      tingkat_aktivitas_p = 1.3
      tingkat_aktivitas_l = 1.3
    elif tingkat_aktivitas == '2':
      tingkat_aktivitas_2 = 'Ringan'
      tingkat_aktivitas_p = 1.55
      tingkat_aktivitas_l = 1.65
    elif tingkat_aktivitas == '3':
      tingkat_aktivitas_2 = 'Sedang'
      tingkat_aktivitas_p = 1.7
      tingkat_aktivitas_l = 1.76
    elif tingkat_aktivitas == '4':
      tingkat_aktivitas_2 = 'Berat'
      tingkat_aktivitas_2 = 'Sedang'
      tingkat_aktivitas_p = 2
      tingkat_aktivitas_l = 2.1
    else:
      tingkat_aktivitas_2 = '-'
    
    if penyakit_penyerta == '1' :
      penyakit_penyerta_2 = 'Kolesterol dalam darah yang tinggi'
    elif penyakit_penyerta == '2':
      penyakit_penyerta_2 = 'Komplikasi pembuluh darah'
    elif penyakit_penyerta == '3':
      penyakit_penyerta_2 = 'lama menderita lebih dari 15 tahun'
    elif penyakit_penyerta == '4':
      penyakit_penyerta_2 = 'Stroke'
    elif penyakit_penyerta == '5':
      penyakit_penyerta_2 = 'Jantung Koroner'
    elif penyakit_penyerta == '6':
      penyakit_penyerta_2 = 'Infark Jantung'
    elif penyakit_penyerta == '7':
      penyakit_penyerta_2 = 'Penyakit pembuluh arteri perifer oklusif'
    elif penyakit_penyerta == '8':
      penyakit_penyerta_2 = 'Gangren'
    else:
      penyakit_penyerta_2 = '-'

    data_personal = {
      'nama'          : nama,
      'jenis_kelamin' : jenis_kelamin_2,
      'berat_badan'   : berat_badan,
      'tinggi_badan'  : tinggi_badan,
      'usia'          : usia,
      'tingkat_aktivitas' : tingkat_aktivitas_2,
      'penyakit_penyerta' : penyakit_penyerta_2,
      'makanan_tidak_suka': makanan_tidak_suka,
      'alergi'            : alergi,
      'kategori_harga'    : kategori_harga,
    }

    bmi = float(berat_badan) /((float(tinggi_badan)*float(tinggi_badan))/10000)

    #Kategori BMI
    if bmi < 17:
      bmi_2 = 'Kekurangan berat badan tingkat berat'
      penambahan_kalori = 1.3 
    elif 17 <= bmi < 18.5:
      bmi_2 = 'Kekurangan berat badan tingkat ringan'
      penambahan_kalori = 1.2
    elif 18.5 <= bmi <= 25:
      bmi_2 = 'Normal'
      penambahan_kalori = 1
    elif 25 < bmi <= 27:
      bmi_2 = 'Kelebihan berat badan tingkat ringan'
      penambahan_kalori = 0.8
    elif bmi > 27:
      bmi_2 = 'Kelebihan berat badan tingkat berat'
      penambahan_kalori = 0.7

    #Metode Harris Benedict
    if jenis_kelamin == 'p':
      amb = 655.096 + ( 9.563 * float(berat_badan)) + ( 1.850 * float(tinggi_badan) ) - (4.676 * float(usia))
      kalori_harian = amb * float(tingkat_aktivitas_p)
    else:
      amb = 66.473 + ( 13.752 * float(berat_badan)) + ( 5.003 * float(tinggi_badan)) - (6.755 * float(usia))
      kalori_harian = amb * float(tingkat_aktivitas_l)
  
    kalori_harian_final = round(kalori_harian * penambahan_kalori, 3)

    #Menghitung zat gizi yang diperlukan 
    total_kalori  = kalori_harian_final
    total_karbo   = round(total_kalori * 0.68 / 4, 3)
    total_protein = round(total_kalori * 0.12 / 4, 3)
    total_lemak   = round(total_kalori * 0.2 / 9, 3)

    data_gizi_harian = {
      'bmi' : bmi,
      'bmi_2' : bmi_2,
      'total_kalori'      : total_kalori,
      'total_karbohidrat' : total_karbo,
      'total_protein'     : total_protein,
      'total_lemak'       : total_lemak
    }

    return render(request, 'menupage.html', {'data_personal': data_personal, 'data_gizi_harian' : data_gizi_harian})
    
  return render(request, 'inputpage.html')