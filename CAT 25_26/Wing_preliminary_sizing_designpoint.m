% Aircraft restrictions
b_m        = 1.75;        % wing span [m]
mTOM_kg    = 6;        % MTOM [kg]

% Speeds & field lengths (sea level unless noted)
Vs_ms      = 11.6;       % stall speed [m/s] (clean, no flaps)
Vc_ms      = 15.5;       % cruise true airspeed [m/s]
STO_m      = 25;         % takeoff ground run requirement [m]

% Performance requirements
ROC_req_ms = 2;        % required rate of climb at climb condition [m/s]
ROC_ceiling_ms = 0.5;    % "service ceiling" ROC threshold [m/s]
    % ---------- Altitude inputs ----------
alt_mode          = "AGL";   % "AGL" or "MSL"
site_elev_m_MSL   = 152;       % set your field elevation (MSL). Example: 120

% Give inputs in the chosen mode:
h_climb_in_m      = 0;       % climb-altitude target (AGL or MSL per alt_mode)
h_ceiling_in_m    = 61;      % service-ceiling altitude limit (AGL or MSL per alt_mode)

% Convert to MSL for the ISA model:
if alt_mode == "AGL"
    h_climb_m   = site_elev_m_MSL + h_climb_in_m;
    h_ceiling_m = site_elev_m_MSL + h_ceiling_in_m;
else
    h_climb_m   = h_climb_in_m;
    h_ceiling_m = h_ceiling_in_m;
end

% Aerodynamics & propulsive assumptions
CLmax_clean = 1.46;      % airfoil/airframe CLmax in clean config (no flaps)
CDo         = 0.025;     % zero-lift drag coefficient (clean)
e_oswald    = 0.85;      % Oswald factor
etaP        = 0.80;      % propulsive efficiency
CDo_LG      = 0.008;     % gear drag increment (TO)
CDo_HLD_TO  = 0.000;     % high-lift device increment at TO (0, since no flaps)
mu_runway   = 0.1;      % ground friction (dry concrete ~0.03–0.05)

% Speed factors
Vmax_factor = 1.3;      % Vmax ≈ 1.2–1.3 Vc
VR_factor   = 1.15;      % rotation speed ~ 1.1–1.2 Vs
Vcl_factor  = 1.30;      % climb sizing speed ~ 1.2–1.4 Vs

% Plot & sweep controls
Npts_sweep  = 350;       % resolution across W/S
make_plot   = true;
isa_rho = @(h_m) 1.225 .* (1 - 2.25577e-5 .* max(h_m,0)).^4.25588;
%% ======================= CONSTANTS / HELPERS ======================== %%
g     = 9.80665;           % m/s^2
rhoSL = isa_rho(site_elev_m_MSL);   % use site density for stall & takeoff lines
% ISA density (simple piecewise up to ~11 km; good enough for sizing)
isa_rho = @(h) rhoSL * (1 - 2.25577e-5*max(h,0)).^4.25588;

W_N = mTOM_kg * g;

%% ===================== STALL-LIMITED W/S CAP ======================= %%
WS_stall = 0.5 * rhoSL * Vs_ms^2 * CLmax_clean;  % [N/m^2] vertical cap

% Sweep wing loading up to (but not including) the stall cap
WS = linspace(max(50,0.4*WS_stall), 0.995*WS_stall, Npts_sweep);  % [N/m^2]

% Preallocations
WP_Vmax = zeros(size(WS));
WP_TO   = zeros(size(WS));
WP_ROC  = zeros(size(WS));
WP_CEIL = zeros(size(WS));
AR_arr  = zeros(size(WS));

%% =================== SPEEDS / DENSITIES FOR CURVES ================= %%
Vmax = Vmax_factor * Vc_ms;
VR   = VR_factor   * Vs_ms;
Vcl  = Vcl_factor  * Vs_ms;

rho_climb  = isa_rho(h_climb_m);
rho_ceil   = isa_rho(h_ceiling_m);

%% ========================= MAIN SWEEP ============================== %%
for i = 1:numel(WS)
    S    = W_N / WS(i);              % wing area from W/S
    AR   = b_m^2 / S;                % aspect ratio from fixed span
    K    = 1/(pi * e_oswald * AR);   % induced-drag factor
    AR_arr(i) = AR;

    % ---- MAX SPEED (prop) -> W/P curve at sea level (or set rho for altitude) ----
    rhoV = rhoSL;  % if Vmax at altitude, replace with isa_rho(h_Vmax)
    term_level_power = 0.5 * rhoV * Vmax^3 * CDo / WS(i) + (2*K/(rhoV*Vmax))*WS(i);
    WP_Vmax(i) = etaP / term_level_power;

    % ---- TAKEOFF GROUND RUN (Sadraey Eqs. 4.66–4.69) -> T/W then to W/P ----
    % Use TO coefficients:
    CDoTO = CDo + CDo_LG + CDo_HLD_TO;
    CLTO  = 0.30 + 0.0;      % clean TO lift coeff ~0.3 baseline (no flaps)
    CDG   = (CDoTO - mu_runway * CLTO);

    % Rotation speed / CL at rotation
    qR    = 0.5 * rhoSL * VR^2;
    CLR   = 2*W_N / (rhoSL * S * VR^2);  % per Sadraey definition

    % Closed-form T/W from ground-run model
    expo  = exp( (0.6 * rhoSL * g * CDG / STO_m) * (S/W_N) );
    TW_TO = mu_runway - (CDG/CLR) .* (expo ./ (1 - expo));   % guard below
    TW_TO = max(TW_TO, 1e-4);

    % Convert to power loading at ~VR
    WP_TO(i) = etaP * VR ./ TW_TO;

    % ---- RATE OF CLIMB (at chosen climb condition, altitude h_climb_m) ----
    q_cl   = 0.5 * rho_climb * Vcl^2;
    D_over_W_cl = q_cl*CDo/WS(i) + K*WS(i)/q_cl;      % (D/W) at climb
    power_per_weight_needed = D_over_W_cl * Vcl + ROC_req_ms;  % (m/s)
    WP_ROC(i) = etaP ./ power_per_weight_needed;

    % ---- SERVICE CEILING (same formula with tiny ROC at altitude) ----
    % For simplicity, use same Vcl factor but at ceiling density.
    q_ceil = 0.5 * rho_ceil * Vcl^2;
    D_over_W_ceil = q_ceil*CDo/WS(i) + K*WS(i)/q_ceil;
    power_per_weight_needed_ceil = D_over_W_ceil * Vcl + ROC_ceiling_ms;
    WP_CEIL(i) = etaP ./ power_per_weight_needed_ceil;
end

%% =================== FEASIBLE ENVELOPE & DESIGN PT ================= %%
% Power-loading requirement is the minimum across all constraints:
WP_req = min( [WP_Vmax; WP_TO; WP_ROC; WP_CEIL], [], 1);

% Best (feasible) design point is the W/S giving the largest W/P (=> min power)
[WP_star, idx_star] = max(WP_req);
WS_star  = WS(idx_star);
S_star   = W_N / WS_star;
AR_star  = AR_arr(idx_star);
P_req_W  = W_N / WP_star;     % Watts
P_req_kW = P_req_W / 1e3;

% Some handy outputs
CL_cruise_est = 2*W_N/(rhoSL*Vc_ms^2*S_star);

%% ============================= PLOTS =============================== %%
if make_plot
    figure; hold on; grid on; box on;
    plot(WS, WP_Vmax, 'LineWidth', 1.8);
    plot(WS, WP_TO,   'LineWidth', 1.8);
    plot(WS, WP_ROC,  'LineWidth', 1.8);
    plot(WS, WP_CEIL, 'LineWidth', 1.8);
    xline(WS_stall, 'r:', 'W/S stall cap', 'LineWidth', 1.2);

    % Feasible ridge & chosen point
    plot(WS, WP_req, 'k--', 'LineWidth', 1.2);
    plot(WS_star, WP_star, 'ko', 'MarkerFaceColor','k', 'DisplayName','Design point');

    xlabel('Wing loading  W/S  [N/m^2]');
    ylabel('Power loading  W/P  [N/W]');
    title('Matching Plot (Props): W/P vs W/S — Stall, TO, V_{max}, ROC, Ceiling');
    legend({'Max speed','Take-off','Rate of climb','Service ceiling','Stall cap','Feasible ridge','Design point'}, ...
           'Location','best');
end

%% =========================== PRINTOUT ============================== %%
fprintf('\n===== Preliminary Design Point (from matching plot) =====\n');
fprintf('Wing loading W/S  : %6.1f N/m^2\n', WS_star);
fprintf('Wing area S       : %6.3f m^2\n', S_star);
fprintf('Aspect ratio AR   : %6.2f (span fixed at %.2f m)\n', AR_star, b_m);
fprintf('Required power    : %6.2f kW  (at sizing point)\n', P_req_kW);
fprintf('Chosen W/P        : %6.4f N/W\n', WP_star);
fprintf('Est. CL_cruise    : %6.3f (sea level)\n', CL_cruise_est);
fprintf('Stall cap W/S     : %6.1f N/m^2\n', WS_stall);

%% ===== MAC & chord geometry (trapezoidal wing) =====
% USER INPUTS
lambda_TR       = 0.55;   % taper ratio λ = c_tip / c_root  (set 1.0 if rectangular)
Lambda_LE_deg   = 0;      % optional leading-edge sweep [deg]; 0 if none

% Known from earlier in your script:
% b_m  -> wingspan [m]
% S_star -> chosen wing area [m^2]

% Chords from S, b, and taper
c_root = 2*S_star / (b_m*(1 + lambda_TR));
c_tip  = lambda_TR * c_root;

% Mean Aerodynamic Chord (length) and its spanwise station from the root
MAC   = (2/3) * c_root * (1 + lambda_TR + lambda_TR^2) / (1 + lambda_TR);
y_MAC = (b_m/6) * (1 + 2*lambda_TR) / (1 + lambda_TR);      % measured along the semi-span from the root

% Optional: x-location of MAC leading edge relative to root LE (uses LE sweep)
x_LE_MAC = y_MAC * tand(Lambda_LE_deg);

% Printout
fprintf('\n===== Planform geometry =====\n');
fprintf('Root chord c_r        : %6.3f m\n', c_root);
fprintf('Tip chord c_t         : %6.3f m\n', c_tip);
fprintf('MAC (length)          : %6.3f m\n', MAC);
fprintf('MAC spanwise station  : %6.3f m from root (%.1f%% of semispan)\n', ...
        y_MAC, 100*y_MAC/(0.5*b_m));
fprintf('MAC LE x-offset       : %6.3f m (from root LE, Λ_LE = %.1f°)\n', x_LE_MAC, Lambda_LE_deg);


% ==================== APPENDIX: INCIDENCE & DECALAGE ==================== %%
% Purpose: compute wing incidence i_w, tail incidence i_t, and decalage Δi.
% Place this block AFTER the matching-plot script (it uses S_star, AR_star, CL_cruise_est).

%% ---------------------- USER INPUTS (EDIT) ---------------------- %%
% Airfoil / wing aerodynamics
aw_1perrad      = 5.7;      % finite-wing lift-curve slope a_w [1/rad]
alphaL0_w_deg   = -2.0;     % wing zero-lift AoA α_L0,w [deg] (clean)

% Tail aerodynamics & sizing (from your tail predesign)
ah_1perrad      = 4.8;      % tail lift-curve slope a_h [1/rad]  (use Eq. 6.57 if you like)
eta_h           = 0.9;      % tail dynamic pressure ratio η_h (~0.85–0.95)
V_H             = 0.6;      % horizontal tail volume coefficient V_H = Sh*lh/(S*cbar)

% Longitudinal stability/trim parameters
Cm0_wf          = -0.05;    % wing+fuselage zero-lift moment coefficient C_m0(wf)
h_bar           = 0.30;     % CG location as fraction of MAC (h)
h0_bar          = 0.25;     % neutral point fraction of MAC (h0)  (preliminary estimate)

% Flight condition for 'cruise' incidence setup
rho_cruise      = 1.225;    % kg/m^3 (set altitude density if needed)
Vc_ms           = Vc_ms;    % reuse from earlier script
theta_fus_deg   = 4;      % desired fuselage pitch attitude at cruise (deg), ~1–3 deg nose-up

% Downwash model choices (Sadraey Eqs. 6.54–6.56)
use_simple_downwash = true; % true = ε0=2*CL/(πAR), dε/dα=2*aw/(πAR)

%% ------------------ DERIVED / FROM PREVIOUS BLOCK ------------------ %%
W_N   = mTOM_kg*9.80665;
S     = S_star;
AR    = AR_star;
CLc   = CL_cruise_est;      % from matching-plot printout
cbar  = S / (b_m);          % mean chord (approx for straight/tapered preliminary)

deg2rad = pi/180; rad2deg = 180/pi;

%% ---------------------- 1) Wing incidence i_w ---------------------- %%
% Wing AoA at cruise from CL = a_w (α_w - α_L0,w)
alpha_w_rad   = (CLc/aw_1perrad) + alphaL0_w_deg*deg2rad;  % α_w = α_L0 + CL/a_w
alpha_w_deg   = alpha_w_rad*rad2deg;

% Set i_w so that fuselage attitude θ_cruise is met: θ = α_w - i_w
i_w_deg       = alpha_w_deg - theta_fus_deg;                % i_w = α_w - θ
% (Wing Step 10: choose incidence to hit the target CL/ideal Cl_i at cruise.)  % Ref: Sadraey Chap 5 steps
% -------------------------------------------------------------------- %

%% ---------------- 2) Tail required CL from trim (Eq. 6.29) --------- %%
% C_m0(wf) + C_L (h - h0) - η_h V_H C_Lh = 0  → C_Lh = [C_m0 + C_L(h-h0)]/(η_h V_H)
CLh_req = (Cm0_wf + CLc*(h_bar - h0_bar)) / (eta_h * V_H);  % Eq. 6.29 (trim)

%% -------------------- 3) Tail AoA from a_h (Eq. 6.51) -------------- %%
alpha_h_req_rad = CLh_req / ah_1perrad;                      % α_h = CLh / a_h
alpha_h_req_deg = alpha_h_req_rad*rad2deg;                   % Eq. 6.51

%% ------------- 4) Downwash at tail (Eqs. 6.54–6.56) ---------------- %%
% Option A: simple lifting-line estimate from Sadraey
use_simple_downwash = true;     % set false to use manual overrides below

% (Only used if use_simple_downwash == false)
eps0_deg_user      = 0.0;       % user-set downwash offset ε0 [deg]
deps_dalpha_user   = 0.40;      % user-set dε/dα [1/rad]  (typ. 0.3–0.6)

if use_simple_downwash
    % ε0 ≈ 2*CL/(π*AR) and dε/dα ≈ 2*a_w/(π*AR)
    eps0_rad    = 2*CLc/(pi*AR);
    deps_dalpha = 2*aw_1perrad/(pi*AR);
else
    % Manual override (e.g., from wind-tunnel/CFD/DATCOM)
    eps0_rad    = eps0_deg_user * deg2rad;
    deps_dalpha = deps_dalpha_user;     % [1/rad]
end

% Aircraft AoA at cruise (≈ wing AoA at cruise)
alpha_aircraft_rad = alpha_w_rad;

% Total downwash at cruise
eps_rad = eps0_rad + deps_dalpha * alpha_aircraft_rad;
%% ------------- 5) Tail incidence i_t from kinematics (Eq. 12.76) ---- %%
% α_h = α + i_t - ε  ⇒  i_t = α_h - α + ε
i_t_rad = alpha_h_req_rad - alpha_aircraft_rad + eps_rad;     % Eq. 12.76
i_t_deg = i_t_rad*rad2deg;

%% ---------------------- 6) Decalage Δi ------------------------------ %%
delta_i_deg = i_w_deg - i_t_deg;

%% --------------------------- REPORT -------------------------------- %%
fprintf('\n===== Incidence & Decalage (cruise trim) =====\n');
fprintf('Cruise CL (from sizing):     %6.4f  [-]\n', CLc);
fprintf('Wing AoA at cruise α_w:      %6.3f  deg\n', alpha_w_deg);
fprintf('Chosen fuselage pitch θ:     %6.3f  deg\n', theta_fus_deg);
fprintf('Wing incidence i_w:          %6.3f  deg\n', i_w_deg);
fprintf('Tail required CL_h (trim):   %6.4f  [-]\n', CLh_req);
fprintf('Tail AoA needed α_h:         %6.3f  deg\n', alpha_h_req_deg);
fprintf('Downwash ε (cruise):         %6.3f  deg\n', eps_rad*rad2deg);
fprintf('Tail incidence i_t:          %6.3f  deg\n', i_t_deg);
fprintf('Decalage Δi = i_w - i_t:     %6.3f  deg  (wing above tail if +)\n', delta_i_deg);
%%

%% ===== Reynolds numbers at cruise & takeoff (uses required CLs) =====
% ISA temperature + Sutherland viscosity (troposphere)
T_atm   = @(h) 288.15 - 0.0065*max(h,0);                              % [K]
mu_suth = @(T) 1.716e-5*(T/273.15).^(3/2) .* (273.15+110.4)./(T+110.4);% [Pa·s]

% Densities (set your cruise altitude if not sea level)
h_cruise_m = site_elev_m_MSL;   % or set to actual cruise MSL altitude
rho_cruise = isa_rho(h_cruise_m);
rho_TO     = isa_rho(site_elev_m_MSL);

% Required lift coefficients at those conditions
CL_cruise_req = 2*W_N/(rho_cruise*Vc_ms^2*S_star);
CL_TO_req     = 2*W_N/(rho_TO*VR^2*S_star);

% Dynamic viscosities via Sutherland's law
mu_cruise = mu_suth(T_atm(h_cruise_m));
mu_TO     = mu_suth(T_atm(site_elev_m_MSL));

% Reynolds numbers based on MAC (use c_tip instead if you want tip Re)
Re_cruise = (rho_cruise * Vc_ms * MAC) / mu_cruise;
Re_TO     = (rho_TO     * VR     * MAC) / mu_TO;

fprintf('\n===== Reynolds numbers =====\n');
fprintf('Re_cruise(MAC):   %.2e   at CL=%.3f, V=%.2f m/s, h=%g m MSL\n', ...
        Re_cruise, CL_cruise_req, Vc_ms, h_cruise_m);
fprintf('Re_takeoff(MAC):  %.2e   at CL=%.3f, V=%.2f m/s, h=%g m MSL\n', ...
        Re_TO,     CL_TO_req,     VR,     site_elev_m_MSL);

%% --- Takeoff AoA & fuselage rotation (paste AFTER incidence block) ---
% Density at takeoff (use your site elevation; if you didn't add isa_rho, set rho_TO = rhoSL)
rho_TO = isa_rho(site_elev_m_MSL);   % or: rho_TO = rhoSL;

% Required CL at rotation (VR)
CL_R = 2*W_N/(rho_TO*VR^2*S_star);

% Wing AoA at liftoff (deg) from airfoil/wing slope and zero-lift angle
alpha_w_TO_deg = alphaL0_w_deg + (CL_R/aw_1perrad)*180/pi;

% Fuselage pitch (deck angle) needed at liftoff (deg)
theta_TO_deg = alpha_w_TO_deg - i_w_deg;

% Optional: average ground-roll AoA if you want a representative rolling attitude
CL_TO_avg = 0.30;  % typical clean value 0.25–0.35 with no flaps
alpha_w_roll_deg = alphaL0_w_deg + (CL_TO_avg/aw_1perrad)*180/pi;
theta_roll_deg   = alpha_w_roll_deg - i_w_deg;

% Sanity check against clean CLmax
if exist('CLmax_clean','var') && CL_R > CLmax_clean
    warning('At VR you need CL_R=%.2f > CLmax_clean=%.2f. Increase VR_factor, raise CLmax, or increase S.', ...
             CL_R, CLmax_clean);
end

fprintf('\n--- Takeoff angles ---\n');
fprintf('CL_R (at VR):           %.3f\n', CL_R);
fprintf('Wing AoA at liftoff:    %.2f deg\n', alpha_w_TO_deg);
fprintf('Fuselage pitch (VR):    %.2f deg\n', theta_TO_deg);
fprintf('Wing AoA (avg roll):    %.2f deg (CL=%.2f)\n', alpha_w_roll_deg, CL_TO_avg);
fprintf('Fuselage pitch (roll):  %.2f deg\n', theta_roll_deg);
