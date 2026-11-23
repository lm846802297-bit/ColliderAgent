! One-case benchmark against the unmodified upstream DDCalc_exampleF.
program native_elastic
  use DDCalc
  use DDExperiments, only: XENON1T_2017_Init
  use DDRates, only: DDCalc_CalcRates
  use DDHalo, only: EToVmin, MeanInverseSpeed, DDCalc_SetHalo
  implicit none
  type(WIMPStruct) :: wimp
  type(HaloStruct) :: halo
  type(DetectorStruct) :: detector
  real(8), parameter :: boosted(10) = [0d0,100d0,250d0,311.999d0,312d0,312.001d0,544d0,775d0,776d0,777d0]
  real(8), parameter :: rest(8) = [0d0,100d0,250d0,543d0,543.999d0,544d0,544.001d0,545d0]
  real(8) :: min_speed(1,1)
  call rate_demo()
  min_speed = EToVmin(1,[8d0],50d0,1,[122d0])
  write(*,'(A,1X,ES25.16E3)') 'vmin', min_speed(1,1)
  call halo_data(232d0,boosted)
  call halo_data(0d0,rest)
contains
  subroutine rate_demo()
    halo = DDCalc_InitHalo()
    wimp = DDCalc_InitWIMP()
    call DDCalc_SetSHM(halo,0.3d0,235d0,235d0,550d0)
    detector = XENON1T_2017_Init()
    call DDCalc_SetWIMP_msigma(wimp,100d0,4d-9,-0.3d-9,2d-5,8d-5)
    call DDCalc_CalcRates(detector,wimp,halo)
    write(*,'(A,1X,I0,3(1X,ES25.16E3))') 'rate',DDCalc_Events(detector), &
       DDCalc_Signal(detector),DDCalc_Background(detector),DDCalc_LogLikelihood(detector)
  end subroutine
  subroutine halo_data(boost,vmin)
    real(8), intent(in) :: boost, vmin(:)
    real(8) :: eta(size(vmin),1)
    integer :: i
    halo = DDCalc_InitHalo()
    ! SetHalo applies vobs before v0, so this sets the final v0 to 220 km/s.
    call DDCalc_SetHalo(halo,vobs=boost,v0=220d0,vesc=544d0,tabulated=.false.)
    eta = MeanInverseSpeed(size(vmin),1,reshape(vmin,[size(vmin),1]),halo)
    do i = 1,size(vmin)
      write(*,'(A,3(1X,ES25.16E3))') 'eta',boost,vmin(i),eta(i,1)
    end do
  end subroutine
end program
