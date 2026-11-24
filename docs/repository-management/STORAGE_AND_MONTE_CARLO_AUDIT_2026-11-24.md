# ColliderAgent storage and Monte Carlo audit — 2026-11-24

**Scope:** read-only repository snapshot audit and adoption of the central three-tier scientific data storage policy.  
**Repository:** `lm846802297-bit/ColliderAgent`  
**Audited branch:** `main`  
**Decision:** retain existing paper assets and history; no bulk migration and no Git LFS activation.

## 1. Repository baseline

- GitHub repository metadata size: **29,504 KiB = 28.81 MiB**.
- Complete recursive main tree: **539 blobs**, **39.12 MiB** summed uncompressed file bytes.
- Recursive tree response was complete (`truncated=false`).
- Files larger than 1 MiB: **6**.
- Files larger than 10 MiB: **0**.
- Files larger than 50 MiB: **0**.
- No root `.gitattributes` or `.lfsconfig` was found.

GitHub repository metadata size and current-tree uncompressed bytes are different measures. The current-tree sum does not include historical-only Git objects or packfile compression and is not a complete historical object-size measurement.

## 2. Largest current files

| Path | Size |
|---|---:|
| `paper-reproduction/1605.02910/paper/1605.02910v2.pdf` | 7.03 MiB |
| `paper-reproduction/2104.05720/paper/2104.05720.pdf` | 3.60 MiB |
| `paper-reproduction/1701.05379/paper/1701.05379v3.pdf` | 3.30 MiB |
| `paper-reproduction/2103.02708/paper/2103.02708/EXO-19-019-authorlist.xml` | 1.51 MiB |
| `paper-reproduction/2103.02708/paper/2103.02708.pdf` | 1.30 MiB |
| `paper-reproduction/1811.07920/1811.07920.pdf` | 1.04 MiB |

The largest files are paper source/reference assets, not native Monte Carlo event outputs.

## 3. Monte Carlo data inventory

The complete current main tree was inspected for native event-data extensions and run/archive naming patterns, including LHE, HepMC, ROOT, Parquet, HDF5, compressed event samples, manifests, and progress records.

- No committed `.lhe`, `.hepmc`, `.root`, `.parquet`, `.h5`, or `.hdf5` event sample was identified in the current tree.
- No large `.gz` or `.zip` event archive was identified.
- The repository contains paper-reproduction assets and code, while the existing ColliderAgent archival extension already requires authoritative paper-specific scientific outputs to be stored in the corresponding project repository where appropriate.
- The local archival extension describes Magnus as an execution backend but correctly prohibits treating a Magnus workspace or expiring Actions artifact as the only permanent result copy.

This is a current-tree inventory, not proof that no historical or external Magnus datasets exist. The audit does not infer external storage locations that are not recorded in the repository.

## 4. Storage-tier decision

### Ordinary Git — retain current contents

Keep source code, model/UFO files, scripts/cards, paper sources, manifests, progress records, provenance, validation reports, processed analysis tables, and reasonably sized outputs in ordinary Git.

The current largest file is 7.03 MiB. No current file approaches GitHub's ordinary-Git per-file warning threshold. No current Monte Carlo event sample was identified that would justify migration.

### Git LFS — not enabled

No root LFS configuration or LFS pointer evidence was identified. Do not enable LFS based on the repository's aggregate size or because the project is a collider simulation toolkit. Evaluate it prospectively only when a concrete large event sample must be versioned with the project and remains practical to retrieve as part of the working set.

### External object storage — not configured

For future bulk LHE/HepMC/ROOT/Parquet event samples or long-term detector-level outputs that are unsuitable for Git/LFS, use durable versioned object storage. Keep immutable object/version ID, URI, byte size, event/record count, source run label, SHA-256, retrieval instructions, and retention responsibility in the repository manifest.

## 5. Standards adoption and local extension

The downstream lock pins central commit `14155487afc075d301fa7f6cf452c7bff137e869`, which includes central PR #42's Git / Git LFS / external object storage policy.

The English and Chinese ColliderAgent archival extensions now express the same three-tier decision rule while preserving project-specific HEP requirements for event-stage separation, event transformations, RCRPS records, source control, and remote SHA-256 verification.

## 6. Integrity and migration boundary

- No existing file was modified, deleted, recompressed, or moved by the audit.
- No Git history was rewritten.
- No Monte Carlo generation or scientific calculation was rerun.
- No LFS configuration was added.
- No external storage provider was selected or configured.
- No existing external event sample was claimed as recovered or independently verified.

## 7. Conclusion

ColliderAgent's current repository snapshot is **39.12 MiB** with no file larger than **7.03 MiB** and no committed native Monte Carlo event sample identified. The current ordinary-Git arrangement is appropriate. **Do not migrate existing paper assets or introduce LFS.** Apply the three-tier policy to future event samples based on actual size, licensing, access, and retention requirements.
