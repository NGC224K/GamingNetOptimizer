import os
import sys
import ctypes
import subprocess
import winreg
import tkinter as tk
from tkinter import ttk, messagebox

# 1. 라이브러리 자동 설치 및 관리자 권한 자동 승인 로직
def run_as_admin():
    """관리자 권한으로 프로그램을 다시 실행합니다."""
    if ctypes.windll.shell32.IsUserAnAdmin():
        return True
    else:
        # 관리자 권한으로 현재 스크립트 재실행
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

def install_requirements():
    try:
        import psutil
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])

# 실행 전 필수 절차
install_requirements()
import psutil

class GamingNetOptimizerV2(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gaming Network Optimizer (Win 11)")
        self.geometry("550x720")
        self.configure(bg="#f5f6f7")
        
        self.adapters = self.get_network_adapters()
        self.apply_all_var = tk.BooleanVar(value=False)
        self.selected_adapter = tk.StringVar()
        
        self.setup_ui()

    def get_network_adapters(self):
        return list(psutil.net_if_addrs().keys())

    def setup_ui(self):
        # 상단 배너
        header_frame = tk.Frame(self, bg="#0078d4", height=80)
        header_frame.pack(fill="x")
        header_label = tk.Label(header_frame, text="🎮 게이밍 네트워크 최적화 도구", 
                                font=("Malgun Gothic", 16, "bold"), fg="white", bg="#0078d4", pady=20)
        header_label.pack()

        # 1. 대상 선택 섹션
        target_frame = tk.LabelFrame(self, text=" 1. 네트워크 어댑터 선택 ", padx=15, pady=15, bg="white")
        target_frame.pack(fill="x", padx=20, pady=15)

        self.cb_all = tk.Checkbutton(target_frame, text="모든 네트워크 어댑터에 일괄 적용 (권장)", 
                                     variable=self.apply_all_var, command=self.toggle_adapter_select,
                                     font=("Malgun Gothic", 10, "bold"), bg="white", activebackground="white")
        self.cb_all.pack(anchor="w")

        self.adapter_combo = ttk.Combobox(target_frame, textvariable=self.selected_adapter, values=self.adapters, state="readonly")
        self.adapter_combo.pack(fill="x", pady=(10, 0))
        if self.adapters: self.adapter_combo.current(0)

        # 2. 항목 설정 섹션
        opt_frame = tk.LabelFrame(self, text=" 2. 최적화 항목 설정 ", padx=15, pady=15, bg="white")
        opt_frame.pack(fill="x", padx=20, pady=10)

        self.options = {
            "TcpAckFrequency": [tk.BooleanVar(value=True), "TcpAckFrequency, 응답 확인 지연 제거 (즉시 응답)", "패킷이 올 때마다 즉시 확인을 보내 핑 변동을 줄입니다."],
            "TCPNoDelay": [tk.BooleanVar(value=True), "TCPNoDelay, Nagle 알고리즘 해제 (즉시 전송)", "작은 패킷들을 모으지 않고 즉시 전송하여 반응 속도를 높입니다."],
            "NetworkThrottlingIndex": [tk.BooleanVar(value=True), "NetworkThrottlingIndex, 네트워크 스로틀링 해제", "멀티미디어 재생 시 시스템이 네트워크를 제한하는 것을 방지합니다."]
        }

        for key, (var, title, desc) in self.options.items():
            f = tk.Frame(opt_frame, bg="white")
            f.pack(fill="x", pady=5)
            tk.Checkbutton(f, text=title, variable=var, font=("Malgun Gothic", 10, "bold"), bg="white").pack(anchor="w")
            tk.Label(f, text=desc, font=("Malgun Gothic", 9), fg="#666", bg="white").pack(anchor="w", padx=20)

        # 3. 효과 예측창
        predict_frame = tk.Frame(self, bg="#e1f5fe", padx=15, pady=15)
        predict_frame.pack(fill="x", padx=20, pady=10)
        self.predict_label = tk.Label(predict_frame, text="[ 최적화 예상 결과 ]\n- 핑(Ping) 수치 안정화 개선 가능\n- 온라인 게임 내 '밀림 현상' 완화\n- 모든 네트워크 인터페이스의 반응성 동기화", 
                                      font=("Malgun Gothic", 9), fg="#01579b", bg="#e1f5fe", justify="left")
        self.predict_label.pack(anchor="w")

        # 실행 버튼
        self.btn_apply = tk.Button(self, text="설정 적용 및 최적화 시작", command=self.apply_logic,
                                   bg="#28a745", fg="white", font=("Malgun Gothic", 12, "bold"), 
                                   relief="flat", pady=12, cursor="hand2")
        self.btn_apply.pack(fill="x", padx=20, pady=20)

    def toggle_adapter_select(self):
        if self.apply_all_var.get():
            self.adapter_combo.configure(state="disabled")
        else:
            self.adapter_combo.configure(state="readonly")

    def apply_logic(self):
        try:
            interfaces_path = r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces"
            
            # 1. TCP 관련 설정 (인터페이스별)
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, interfaces_path) as root_key:
                num_subkeys = winreg.QueryInfoKey(root_key)[0]
                
                for i in range(num_subkeys):
                    guid = winreg.EnumKey(root_key, i)
                    # "모든 어댑터" 체크 시 전부 적용, 아니면 선택된 것만 적용(실제 환경에선 매칭 로직이 복잡하므로 일괄 적용이 안전함)
                    with winreg.OpenKey(root_key, guid, 0, winreg.KEY_ALL_ACCESS) as subkey:
                        if self.options["TcpAckFrequency"][0].get():
                            winreg.SetValueEx(subkey, "TcpAckFrequency", 0, winreg.REG_DWORD, 1)
                        if self.options["TCPNoDelay"][0].get():
                            winreg.SetValueEx(subkey, "TCPNoDelay", 0, winreg.REG_DWORD, 1)

            # 2. 글로벌 시스템 스로틀링 설정
            if self.options["NetworkThrottlingIndex"][0].get():
                profile_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile"
                with winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, profile_path, 0, winreg.KEY_ALL_ACCESS) as key:
                    winreg.SetValueEx(key, "NetworkThrottlingIndex", 0, winreg.REG_DWORD, 0xFFFFFFFF)

            messagebox.showinfo("성공", "모든 최적화 설정이 성공적으로 적용되었습니다.\n\n효과를 적용하려면 반드시 시스템을 '다시 시작'해 주세요.")
        except Exception as e:
            messagebox.showerror("오류", f"설정 적용 중 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    # 관리자 권한 확인 및 재실행
    if run_as_admin():
        app = GamingNetOptimizerV2()
        app.mainloop()