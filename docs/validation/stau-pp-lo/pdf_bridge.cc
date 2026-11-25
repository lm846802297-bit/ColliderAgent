#include <LHAPDF/LHAPDF.h>
#include <memory>
#include <cmath>
static std::unique_ptr<LHAPDF::PDF> pdf;
extern "C" int pdf_init(const char* dir) {
  try {
    LHAPDF::setVerbosity(0);
    LHAPDF::pathsPrepend(dir);
    pdf.reset(LHAPDF::mkPDF("NNPDF23_lo_as_0130_qed",0));
    pdf->setForcePositive(0);
    return 0;
  } catch (...) { return 1; }
}
extern "C" int pdf_light(double x, double q, double* out) {
  try {
    if (!pdf || !pdf->inRangeXQ(x,q)) return 1;
    for (int pid=1; pid<=5; ++pid) {
      out[2*(pid-1)]=pdf->xfxQ(pid,x,q);
      out[2*(pid-1)+1]=pdf->xfxQ(-pid,x,q);
    }
    for(int i=0;i<10;++i) if (!std::isfinite(out[i])) return 2;
    return 0;
  } catch (...) { return 3; }
}
